import { chromium, FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  // Create artifacts directory structure
  const artifactsDir = path.join(process.cwd(), 'artifacts', 'e2e');
  
  // Ensure base artifacts directory exists
  if (!fs.existsSync(artifactsDir)) {
    fs.mkdirSync(artifactsDir, { recursive: true });
  }
  
  // Create subdirectories for different artifact types
  const subdirs = ['har', 'screenshots', 'videos', 'traces'];
  subdirs.forEach(subdir => {
    const subdirPath = path.join(artifactsDir, subdir);
    if (!fs.existsSync(subdirPath)) {
      fs.mkdirSync(subdirPath, { recursive: true });
    }
  });
  
  console.log('✅ Global setup completed - artifacts directory structure created');
}

export default globalSetup;
