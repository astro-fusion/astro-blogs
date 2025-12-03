const fs = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');
const chalk = require('chalk');

const TARGET_DIR = '06_Planet_in_Houses/0601_Sun_in_Houses';
const IGNORE_FILES = ['060100_sun_knowledge.mdx'];

const REQUIRED_TAGS = [
  'Prediction:Career:General',
  'Prediction:Finance:Income',
  'Prediction:Finance:Expenses',
  'Prediction:Relationships:Romantic',
  'Prediction:Relationships:Family',
  'Prediction:Health:Physical',
  'Prediction:Health:Mental',
  'Prediction:Education:Academic',
  'Prediction:Travel:Domestic',
  'Prediction:Travel:Foreign',
  'Prediction:Spirituality:Practice',
  'Prediction:Spirituality:Karma'
];

async function validateFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const errors = [];
  const fileName = path.basename(filePath);

  if (IGNORE_FILES.includes(fileName)) return errors;

  // 1. Validate Frontmatter
  const { data, content: mdxContent } = matter(content);
  if (!data.title) errors.push('Missing "title" in frontmatter');

  // 2. Validate Predictions Section
  if (!mdxContent.includes('## Predictions by Life Area')) {
    errors.push('Missing "## Predictions by Life Area" section');
  } else {
    // Check for each tag
    REQUIRED_TAGS.forEach(tag => {
      if (!mdxContent.includes(`### ${tag}`)) {
        errors.push(`Missing tag: ### ${tag}`);
      }
    });
  }

  return errors;
}

async function run() {
  console.log(chalk.blue(`Starting Prediction Validation for ${TARGET_DIR}...`));

  const projectRoot = path.join(__dirname, '..');
  // Only look in the specific Sun directory
  const pattern = path.join(TARGET_DIR, '*.mdx');
  const files = glob.sync(pattern, { cwd: projectRoot, absolute: true });
  
  let hasErrors = false;
  let processedCount = 0;

  for (const file of files) {
    processedCount++;
    const errors = await validateFile(file);

    if (errors.length > 0) {
      hasErrors = true;
      console.log(chalk.red(`
❌ Error in ${path.basename(file)}:`));
      errors.forEach(err => console.log(chalk.yellow(`  - ${err}`)));
    } else {
      process.stdout.write(chalk.green('.'));
    }
  }

  console.log(chalk.blue(`

Processed ${processedCount} files.`));

  if (hasErrors) {
    console.log(chalk.red('
Validation Failed! Please fix the errors above.'));
    process.exit(1);
  } else {
    console.log(chalk.green('
✅ Validation Passed! All files look good.'));
    process.exit(0);
  }
}

run().catch(err => {
  console.error(chalk.red('Fatal Error:'), err);
  process.exit(1);
});