const fs = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');
const { compile } = require('@mdx-js/mdx');
const chalk = require('chalk');
const remarkMath = require('remark-math');
const rehypeKatex = require('rehype-katex');

const MDX_PATTERN = '**/*.mdx';
const IGNORE_PATTERN = ['node_modules/**', 'README.md'];

async function validateFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const errors = [];

  // 1. Validate Frontmatter
  const { data, content: mdxContent } = matter(content);

  if (!data.title) errors.push('Missing "title" in frontmatter');
  if (!data.description) errors.push('Missing "description" in frontmatter');
  if (!data.keywords) errors.push('Missing "keywords" in frontmatter');

  // 2. Validate MDX Syntax
  try {
    await compile(mdxContent, {
      remarkPlugins: [remarkMath.default],
      rehypePlugins: [rehypeKatex.default]
    });
  } catch (err) {
    errors.push(`MDX Syntax Error: ${err.message}`);
  }

  return errors;
}

async function run() {
  console.log(chalk.blue('Starting MDX Validation...'));

  const projectRoot = path.join(__dirname, '..');
  const files = glob.sync(MDX_PATTERN, { cwd: projectRoot, ignore: IGNORE_PATTERN, absolute: true });
  let hasErrors = false;
  let processedCount = 0;

  for (const file of files) {
    processedCount++;
    const errors = await validateFile(file);

    if (errors.length > 0) {
      hasErrors = true;
      console.log(chalk.red(`\n❌ Error in ${file}:`));
      errors.forEach(err => console.log(chalk.yellow(`  - ${err}`)));
    } else {
      // Optional: Log success for verbose mode, or just a dot
      process.stdout.write(chalk.green('.'));
    }
  }

  console.log(chalk.blue(`\n\nProcessed ${processedCount} files.`));

  if (hasErrors) {
    console.log(chalk.red('\nValidation Failed! Please fix the errors above.'));
    process.exit(1);
  } else {
    console.log(chalk.green('\n✅ Validation Passed! All files look good.'));
    process.exit(0);
  }
}

run().catch(err => {
  console.error(chalk.red('Fatal Error:'), err);
  process.exit(1);
});
