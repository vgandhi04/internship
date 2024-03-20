

# Git Workflow with Visual Studio Code

## 1. Create a New Branch

```bash
# Create and switch to the dev branch
git checkout -b dev
```

## 2. Work on the Dev Branch

Make your changes in this branch.

### 2.1 if already in dev branch
```bash
# Switch to the dev branch
git checkout dev

# Fetch the latest changes from the remote dev branch and merge them into your local dev branch
git pull origin dev
```
## 3. Commit Your Changes

```bash
# Stage changes
git add .

# Commit changes
git commit -m "Your commit message"
```

## 4. Push Changes to Dev Branch

```bash
# Push changes to the remote dev branch
git push origin dev
```

## 5. Switch to the Main Branch

```bash
# Switch to the main branch
git checkout main
```

## 6. Merge Changes from Dev to Main

```bash
# Merge changes from dev to main
git merge dev
```

## 7. Push Changes to Main Branch

```bash
# Push changes to the remote main branch
git push origin main
```

## 8. Switch Back to the Dev Branch

```bash
# Switch back to the dev branch
git checkout dev
```

Repeat these steps as needed for your workflow. Resolve any conflicts during the merge process.
