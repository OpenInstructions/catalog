#!/usr/bin/env node

/**
 * OpenInstructions Catalog Build Script
 * 
 * This script generates a versioned directory structure based on version fields in YAML files.
 * It creates the necessary symlinks and ensures consistent versioning across the catalog.
 * 
 * Usage: node build.js [output-dir]
 * Default output directory is './dist'
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const glob = require('glob');

// Configuration
const CONFIG = {
  // Source directories to process
  sourceDirs: ['./migrated/schemas', './migrated/project_types'],
  
  // Output directory for the build
  outputDir: process.argv[2] || './dist',
  
  // Base path for the catalog
  catalogBasePath: 'catalog',
  
  // Patterns to find all YAML files
  yamlPattern: '**/*.yaml',

  // Versioning setup
  catalogVersionPrefix: 'v',  // prefix for catalog version directories (e.g., v1, v2)
  instructionVersionPrefix: 'v',  // prefix for instruction version directories (e.g., v1.0, v1.1)
};

/**
 * Main build function
 */
async function build() {
  console.log('🔨 Building OpenInstructions Catalog...');
  
  // Create output directory if it doesn't exist
  const fullOutputDir = path.join(CONFIG.outputDir, CONFIG.catalogBasePath);
  fs.mkdirSync(fullOutputDir, { recursive: true });
  
  // Discover all YAML files
  const yamlFiles = await discoverYamlFiles();
  console.log(`📄 Found ${yamlFiles.length} YAML files to process`);
  
  // Parse all files and extract version information
  const fileData = parseYamlFiles(yamlFiles);
  
  // Organize files by catalog version
  const catalogVersions = organizeByCatalogVersion(fileData);
  
  // Create catalog version directories and latest symlink
  createCatalogVersionDirs(catalogVersions, fullOutputDir);
  
  // Process each file and create the versioned structure
  await processFiles(fileData, fullOutputDir);
  
  console.log('✅ Catalog build complete!');
}

/**
 * Discover all YAML files in source directories
 */
async function discoverYamlFiles() {
  const yamlFiles = [];
  
  for (const sourceDir of CONFIG.sourceDirs) {
    const pattern = path.join(sourceDir, CONFIG.yamlPattern);
    const files = glob.sync(pattern);
    yamlFiles.push(...files);
  }
  
  return yamlFiles;
}

/**
 * Parse YAML files and extract version information
 */
function parseYamlFiles(files) {
  const fileData = [];
  
  for (const file of files) {
    try {
      const content = fs.readFileSync(file, 'utf8');
      const data = yaml.load(content);
      
      // Extract version information
      const catalogVersion = data.catalog_version || '0.1.0';  // Default if not specified
      const instructionVersion = data.version || '0.1.0';  // Default if not specified
      
      fileData.push({
        sourcePath: file,
        content,
        data,
        catalogVersion,
        instructionVersion,
        // Extract type information from path for organizing
        projectType: extractProjectTypeInfo(file),
      });
      
    } catch (error) {
      console.error(`❌ Error parsing ${file}:`, error.message);
    }
  }
  
  return fileData;
}

/**
 * Extract project type information from file path
 */
function extractProjectTypeInfo(filePath) {
  // Handle schema files
  if (filePath.includes('schemas/')) {
    return {
      type: 'schema',
      name: path.basename(filePath, '.yaml'),
    };
  }
  
  // Handle project type files
  const parts = filePath.split('/');
  const projectTypeIndex = parts.indexOf('project_types');
  
  if (projectTypeIndex >= 0 && parts.length > projectTypeIndex + 1) {
    const info = {
      type: 'project',
      projectType: parts[projectTypeIndex + 1],
      variants: [],
    };
    
    // Extract variant information
    for (let i = projectTypeIndex + 2; i < parts.length - 1; i++) {
      info.variants.push(parts[i]);
    }
    
    info.filename = parts[parts.length - 1];
    
    return info;
  }
  
  return { type: 'unknown', path: filePath };
}

/**
 * Organize files by catalog version
 */
function organizeByCatalogVersion(fileData) {
  const versions = new Set();
  
  for (const file of fileData) {
    versions.add(file.catalogVersion);
  }
  
  return Array.from(versions).sort();
}

/**
 * Create catalog version directories and set up latest symlink
 */
function createCatalogVersionDirs(catalogVersions, outputDir) {
  if (catalogVersions.length === 0) {
    console.warn('⚠️ No catalog versions found');
    return;
  }
  
  // Create directory for each catalog version
  for (const version of catalogVersions) {
    const versionDir = path.join(
      outputDir, 
      `${CONFIG.catalogVersionPrefix}${version.split('.')[0]}`
    );
    fs.mkdirSync(versionDir, { recursive: true });
    console.log(`📁 Created catalog version directory: ${versionDir}`);
  }
  
  // Create 'latest' symlink pointing to the highest version
  const latestVersion = catalogVersions[catalogVersions.length - 1];
  const latestDir = `${CONFIG.catalogVersionPrefix}${latestVersion.split('.')[0]}`;
  const symlinkPath = path.join(outputDir, 'latest');
  
  try {
    // Remove existing symlink if it exists
    if (fs.existsSync(symlinkPath)) {
      try {
        fs.unlinkSync(symlinkPath);
      } catch (error) {
        console.warn(`⚠️ Could not remove existing symlink ${symlinkPath}: ${error.message}`);
      }
    }
    
    // Create new symlink
    fs.symlinkSync(latestDir, symlinkPath, 'dir');
    console.log(`🔗 Created 'latest' symlink to ${latestDir}`);
  } catch (error) {
    console.warn(`⚠️ Could not create 'latest' symlink: ${error.message}`);
  }
}

/**
 * Process each file and create the versioned structure
 */
async function processFiles(fileData, outputDir) {
  // Track instruction versions by path pattern for creating 'latest' symlinks
  const instructionVersions = {};
  
  // First pass: copy all files to their versioned locations
  for (const file of fileData) {
    try {
      const { sourcePath, content, catalogVersion, instructionVersion, projectType } = file;
      
      // Determine the target directory
      let targetDir;
      let targetFilename;
      
      if (projectType.type === 'schema') {
        // Schema files go directly under the catalog version
        targetDir = path.join(
          outputDir,
          `${CONFIG.catalogVersionPrefix}${catalogVersion.split('.')[0]}`,
          'schemas'
        );
        targetFilename = path.basename(sourcePath);
      } else if (projectType.type === 'project') {
        // Project files go into their versioned directories
        const catalogVersionDir = `${CONFIG.catalogVersionPrefix}${catalogVersion.split('.')[0]}`;
        const instructionVersionDir = `${CONFIG.instructionVersionPrefix}${instructionVersion.split('.')[0]}.${instructionVersion.split('.')[1]}`;
        
        // Build the full path
        const pathParts = [
          outputDir,
          catalogVersionDir,
          'project_types',
          projectType.projectType,
          ...projectType.variants,
          instructionVersionDir
        ];
        
        targetDir = path.join(...pathParts);
        targetFilename = projectType.filename;
        
        // Track instruction versions for creating 'latest' symlinks
        const versionTrackingKey = pathParts.slice(0, -1).join('/');
        if (!instructionVersions[versionTrackingKey]) {
          instructionVersions[versionTrackingKey] = [];
        }
        instructionVersions[versionTrackingKey].push({
          version: instructionVersion,
          versionDir: instructionVersionDir
        });
      } else {
        console.warn(`⚠️ Unknown file type: ${sourcePath}`);
        continue;
      }
      
      // Create the target directory
      fs.mkdirSync(targetDir, { recursive: true });
      
      // Write the content to the target location
      const targetPath = path.join(targetDir, targetFilename);
      fs.writeFileSync(targetPath, content);
      
      console.log(`📝 Copied ${sourcePath} to ${targetPath}`);
      
    } catch (error) {
      console.error(`❌ Error processing ${file.sourcePath}:`, error.message);
    }
  }
  
  // Second pass: create 'latest' symlinks for instruction versions
  for (const [dirPath, versions] of Object.entries(instructionVersions)) {
    if (versions.length === 0) continue;
    
    // Sort versions to find the highest
    versions.sort((a, b) => {
      const aParts = a.version.split('.').map(Number);
      const bParts = b.version.split('.').map(Number);
      
      if (aParts[0] !== bParts[0]) return aParts[0] - bParts[0];
      if (aParts[1] !== bParts[1]) return aParts[1] - bParts[1];
      return aParts[2] - bParts[2];
    });
    
    const latestVersion = versions[versions.length - 1];
    
    // Create 'latest' symlink
    const symlinkPath = path.join(dirPath, 'latest');
    
    // Remove existing symlink if it exists
    try {
      if (fs.existsSync(symlinkPath)) {
        try {
          fs.unlinkSync(symlinkPath);
        } catch (error) {
          console.warn(`⚠️ Could not remove existing symlink ${symlinkPath}: ${error.message}`);
          console.warn('Skipping this symlink...');
          continue;
        }
      }
      
      // Create new symlink
      fs.symlinkSync(latestVersion.versionDir, symlinkPath, 'dir');
      console.log(`🔗 Created 'latest' symlink in ${dirPath} to ${latestVersion.versionDir}`);
    } catch (error) {
      console.warn(`⚠️ Could not create symlink in ${dirPath}: ${error.message}`);
    }
  }
}

// Run the build
build().catch(error => {
  console.error('❌ Build failed:', error);
  process.exit(1);
}); 