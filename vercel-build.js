const { execSync } = require('child_process');
const fs = require('fs');

// Set Python version
console.log('Setting Python version to 3.12...');
fs.writeFileSync('runtime.txt', '3.12.0');

// Install dependencies
console.log('Installing dependencies...');
try {
  // Ensure pip is up to date
  execSync('python3.12 -m pip install --upgrade pip', { stdio: 'inherit' });
  
  // Install build dependencies first
  execSync('python3.12 -m pip install --upgrade setuptools wheel', { stdio: 'inherit' });
  
  // Install requirements
  execSync('python3.12 -m pip install -r requirements.txt', { stdio: 'inherit' });
  
  console.log('Build completed successfully!');
} catch (error) {
  console.error('Build failed:', error);
  process.exit(1);
}
