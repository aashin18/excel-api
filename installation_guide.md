# Git and Heroku CLI Installation Guide

## Installing Git

### Windows
1. Download the Git installer from the official website: https://git-scm.com/download/win
   - For most Windows PCs (Intel or AMD processors): Choose the "64-bit Git for Windows Setup" option
   - For Windows ARM devices (like Surface Pro X or Windows devices with Qualcomm Snapdragon): Choose the "ARM64 Git for Windows Setup" option
   - To check your processor type:
     - Right-click on Start button > System
     - Look under "Device specifications" > "Processor" 
     - If it mentions "ARM" anywhere, download the ARM version
     - Otherwise, use the standard 64-bit version

2. Run the downloaded executable (.exe) file
3. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation location (default is recommended)
   - Select components (default options are usually fine)
   - Choose the default editor (Notepad++ or VS Code recommended if you have them)
   - Adjust your PATH environment (select "Git from the command line and also from 3rd-party software")
   - Choose HTTPS transport backend (use the native Windows Secure Channel library)
   - Configure line ending conversions (recommended: "Checkout Windows-style, commit Unix-style")
   - Configure terminal emulator (use MinTTY)
   - Configure extra options (default options are fine)
   - Configure experimental options (no need to enable)
4. Click Install and wait for the installation to complete
5. Verify installation by opening Command Prompt or PowerShell and typing:
   ```
   git --version
   ```

### macOS
1. Install Git using one of these methods:
   - Install Xcode Command Line Tools which includes Git:
     ```
     xcode-select --install
     ```
   - Or install via Homebrew:
     ```
     brew install git
     ```
2. Verify installation:
   ```
   git --version
   ```

### Linux (Ubuntu/Debian)
1. Open Terminal
2. Update package lists:
   ```
   sudo apt update
   ```
3. Install Git:
   ```
   sudo apt install git
   ```
4. Verify installation:
   ```
   git --version
   ```

## Installing Heroku CLI

### Windows
1. Download the Heroku CLI installer from the official website: https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
   - Choose "Download the installer" (the main .exe installer)
   - NOT the "First time Git setup" - that's for a different purpose
   - The main installer will handle everything you need including Git integration
2. Run the downloaded executable (.exe) file **as Administrator** (right-click > "Run as administrator")
3. Follow the installation wizard with default settings
4. **IMPORTANT**: After installation, completely close all PowerShell/Command Prompt windows and reopen them
5. Verify installation:
   ```
   heroku --version
   ```

**If you still get "heroku is not recognized":**
1. Close all terminal windows
2. Press Windows key + R, type `cmd`, press Enter
3. Try `heroku --version` again
4. If it still doesn't work, manually add Heroku to your PATH:
   - Press Windows key + X, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - In "System Variables", find and select "Path", click "Edit"
   - Click "New" and add: `C:\Program Files\heroku\bin`
   - Click OK to save
   - Restart your computer
   - Try `heroku --version` again

### macOS
1. Install using Homebrew:
   ```
   brew tap heroku/brew && brew install heroku
   ```
2. Or download the installer from: https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
3. Verify installation:
   ```
   heroku --version
   ```

### Linux (Ubuntu/Debian)
1. Run the installation script:
   ```
   curl https://cli-assets.heroku.com/install.sh | sh
   ```
2. Or install via snap:
   ```
   sudo snap install --classic heroku
   ```
3. Verify installation:
   ```
   heroku --version
   ```

## Setting Up Git and Heroku

After installing both tools:

1. Configure Git with your identity:
   ```
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. Login to Heroku:
   ```
   heroku login
   ```
   This will open a browser window where you'll need to log in to your Heroku account.

3. Now you're ready to create and deploy your application to Heroku!
```
cd c:\Users\AASHIN\OneDrive - Heriot-Watt University\Desktop\python
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

If your default branch is "master" instead of "main", use:
```
git push heroku master
```

## Troubleshooting

### Common Git Issues
- **'git' is not recognized as an internal or external command**: Restart your terminal/command prompt after installation or add Git to your PATH manually.
- **Permission denied errors**: Use `sudo` for commands on Linux/macOS or run command prompt as administrator on Windows.

### Common Heroku CLI Issues
- **'heroku' is not recognized as a command**: 
  1. First, completely close and reopen your terminal/PowerShell
  2. If that doesn't work, manually add Heroku to your PATH (see Windows installation steps above)
  3. Restart your computer if necessary
- **Authentication failures**: Run `heroku login` again to refresh your credentials.
- **Deployment failures**: Ensure your application has the required files (Procfile, requirements.txt for Python apps).

### Quick Fix for "heroku not recognized" error:
Try these steps in order:
1. Close all terminal windows and reopen
2. Try a regular Command Prompt instead of PowerShell
3. Restart your computer
4. Manually add to PATH (see detailed steps in Windows installation section above)
