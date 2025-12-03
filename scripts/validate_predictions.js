const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const chalk = require('chalk');

// Configuration - can be overridden via command line argument
const TARGET_DIR = process.argv[2] || '06_Planet_in_Houses/0601_Sun_in_Houses';

/**
 * Validate prediction-focused content in astrology files
 */
function validatePredictions(filePath) {
  const errors = [];
  const warnings = [];

  try {
    const content = fs.readFileSync(filePath, 'utf8');

    // 1. Basic frontmatter validation
    const { data, content: mdxContent } = matter(content);

    if (!data.title) errors.push('Missing "title" in frontmatter');
    if (!data.description) errors.push('Missing "description" in frontmatter');

    // 2. Check for "Predictions by Life Area" section (new standardized section)
    const hasPredictionsSection = mdxContent.includes('## Predictions by Life Area');
    if (!hasPredictionsSection) {
      warnings.push('Missing "## Predictions by Life Area" section - consider adding this standardized section');
    }

    // 3. If predictions section exists, validate its structure
    if (hasPredictionsSection) {
      const predictionsIndex = mdxContent.indexOf('## Predictions by Life Area');
      const afterPredictions = mdxContent.substring(predictionsIndex);

      // Check for common life areas that should be covered
      const lifeAreas = [
        'Career',
        'Finance',
        'Health',
        'Relationships',
        'Marriage',
        'Education',
        'Family',
        'Spiritual'
      ];

      const foundAreas = lifeAreas.filter(area =>
        afterPredictions.toLowerCase().includes(area.toLowerCase())
      );

      if (foundAreas.length < 3) {
        warnings.push('Predictions section seems limited. Consider covering more life areas (Career, Finance, Health, Relationships, etc.)');
      }

      // Check for proper subheadings under predictions
      const subheadingRegex = /^### .*$/gm;
      const subheadings = afterPredictions.match(subheadingRegex) || [];
      if (subheadings.length < 2) {
        warnings.push('Predictions section could benefit from more detailed subheadings (### level)');
      }
    }

    // 4. Check for prediction keywords and patterns
    const predictionKeywords = [
      'effects', 'impact', 'influence', 'beneficial', 'challenging',
      'positive', 'negative', 'favorable', 'unfavorable', 'strength',
      'weakness', 'remedies', 'solutions'
    ];

    const contentWords = mdxContent.toLowerCase();
    const foundKeywords = predictionKeywords.filter(keyword =>
      contentWords.includes(keyword)
    );

    if (foundKeywords.length < 5) {
      warnings.push('Content could be more prediction-focused. Consider using more predictive language.');
    }

    // 5. Check for balance between positive and negative predictions
    const positiveWords = ['beneficial', 'favorable', 'positive', 'strength', 'success'];
    const negativeWords = ['challenging', 'unfavorable', 'negative', 'weakness', 'difficult'];

    const positiveCount = positiveWords.filter(word => contentWords.includes(word)).length;
    const negativeCount = negativeWords.filter(word => contentWords.includes(word)).length;

    if (positiveCount === 0 && negativeCount === 0) {
      warnings.push('Consider providing more balanced predictions (both positive and challenging aspects)');
    }

    // 6. Check for remedy suggestions
    const remedyIndicators = ['remedies', 'solutions', 'mitigate', 'balance', 'mantra', 'gemstone'];
    const hasRemedies = remedyIndicators.some(indicator => contentWords.includes(indicator));

    if (!hasRemedies) {
      warnings.push('Consider adding remedy suggestions for challenging predictions');
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

  console.log(chalk.blue(`Starting predictions validation for: ${targetDir}`));

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
    const { errors, warnings } = validatePredictions(file);

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

  console.log(chalk.blue(`\nPredictions Validation Summary:`));
  console.log(chalk.red(`Errors: ${totalErrors}`));
  console.log(chalk.yellow(`Warnings: ${totalWarnings}`));

  if (totalErrors > 0) {
    console.log(chalk.red('\nValidation failed! Please fix the errors above.'));
    process.exit(1);
  } else if (totalWarnings > 0) {
    console.log(chalk.yellow('\nValidation passed with warnings. Consider addressing them for better prediction quality.'));
    process.exit(0);
  } else {
    console.log(chalk.green('\n✅ Predictions validation passed! All files look good.'));
    process.exit(0);
  }
}

// Run validation
validateDirectory(TARGET_DIR);
