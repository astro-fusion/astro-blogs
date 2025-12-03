const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const chalk = require('chalk');

// Configuration - can be overridden via command line argument
const TARGET_DIR = process.argv[2] || '06_Planet_in_Houses/0609_Ketu_in_Houses';

/**
 * Validate advanced aspects of astrology content files
 */
function validateFile(filePath) {
  const errors = [];
  const warnings = [];

  try {
    const content = fs.readFileSync(filePath, 'utf8');

    // 1. Validate Frontmatter
    const { data, content: mdxContent } = matter(content);

    if (!data.title) errors.push('Missing "title" in frontmatter');
    if (!data.description) errors.push('Missing "description" in frontmatter');
    if (!data.pubDate) errors.push('Missing "pubDate" in frontmatter');

    // 2. Validate content structure for astrology blogs
    const lines = mdxContent.split('\n');

    // Check for required sections
    const hasKeywords = mdxContent.includes('## Keywords');
    const hasSummary = mdxContent.includes('## Summary');
    const hasPredictions = mdxContent.includes('## Predictions by Life Area') ||
                          mdxContent.includes('## Effects') ||
                          mdxContent.includes('## Transit Effects');

    if (!hasKeywords) errors.push('Missing "## Keywords" section');
    if (!hasSummary) errors.push('Missing "## Summary" section');
    if (!hasPredictions) warnings.push('Consider adding "## Predictions by Life Area" section for better structure');

    // 3. Check for broken internal links
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;
    while ((match = linkRegex.exec(content)) !== null) {
      const linkText = match[1];
      const linkUrl = match[2];

      // Check internal links
      if (linkUrl.endsWith('.md') && !linkUrl.startsWith('http')) {
        const linkPath = path.resolve(path.dirname(filePath), linkUrl);
        if (!fs.existsSync(linkPath)) {
          errors.push(`Broken internal link: [${linkText}](${linkUrl})`);
        }
      }
    }

    // 4. Check for proper heading hierarchy
    let lastHeadingLevel = 0;
    for (const line of lines) {
      if (line.startsWith('#')) {
        const level = line.match(/^#+/)[0].length;
        if (level > lastHeadingLevel + 1) {
          warnings.push(`Skipped heading level: "${line.trim()}" (jumped from H${lastHeadingLevel} to H${level})`);
        }
        lastHeadingLevel = level;
      }
    }

    // 5. Check for minimum content length
    const cleanContent = mdxContent.replace(/^\s*#.*$/gm, '').trim();
    if (cleanContent.length < 500) {
      warnings.push('Content seems short (< 500 characters). Consider adding more detail.');
    }

  } catch (err) {
    errors.push(`Failed to read file: ${err.message}`);
  }

  return { errors, warnings };
}

function validateDirectory(targetDir) {
  const projectRoot = path.join(__dirname, '..');
  const fullTargetPath = path.join(projectRoot, targetDir);

  if (!fs.existsSync(fullTargetPath)) {
    console.error(chalk.red(`Target directory does not exist: ${fullTargetPath}`));
    process.exit(1);
  }

  console.log(chalk.blue(`Starting advanced validation for: ${targetDir}`));

  const files = fs.readdirSync(fullTargetPath)
    .filter(file => file.endsWith('.mdx') || file.endsWith('.md'))
    .map(file => path.join(fullTargetPath, file));

  if (files.length === 0) {
    console.log(chalk.yellow(`No .md or .mdx files found in ${targetDir}`));
    return;
  }

  let totalErrors = 0;
  let totalWarnings = 0;

  for (const file of files) {
    const relativePath = path.relative(projectRoot, file);
    const { errors, warnings } = validateFile(file);

    if (errors.length > 0 || warnings.length > 0) {
      console.log(chalk.red(`\n❌ ${relativePath}:`));

      errors.forEach(err => {
        console.log(chalk.red(`  - Error: ${err}`));
        totalErrors++;
      });

      warnings.forEach(warn => {
        console.log(chalk.yellow(`  - Warning: ${warn}`));
        totalWarnings++;
      });
    } else {
      console.log(chalk.green(`✅ ${relativePath}: OK`));
    }
  }

  console.log(chalk.blue(`\nValidation Summary:`));
  console.log(chalk.red(`Errors: ${totalErrors}`));
  console.log(chalk.yellow(`Warnings: ${totalWarnings}`));

  if (totalErrors > 0) {
    console.log(chalk.red('\nValidation failed! Please fix the errors above.'));
    process.exit(1);
  } else if (totalWarnings > 0) {
    console.log(chalk.yellow('\nValidation passed with warnings. Consider addressing them for better quality.'));
    process.exit(0);
  } else {
    console.log(chalk.green('\n✅ Advanced validation passed! All files look good.'));
    process.exit(0);
  }
}

// Run validation
validateDirectory(TARGET_DIR);
