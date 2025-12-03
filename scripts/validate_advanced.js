const fs = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');
const { compile } = require('@mdx-js/mdx');
const chalk = require('chalk');

// Configuration
const TARGET_DIR = '06_Planet_in_Houses/0609_Ketu_in_Houses';
const IGNORE_FILES = ['060900_Ketu_in_Houses.mdx', '060900_ketu_in_sign.mdx', '_meta.json'];

const REQUIRED_FM_FIELDS = [
    'title',
    'description',
    'keywords'
];

const PREDICTION_TAGS = [
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
    const errors = [];
    const warnings = [];
    const fileName = path.basename(filePath);

    if (IGNORE_FILES.includes(fileName)) return { errors, warnings };

    let content;
    try {
        content = fs.readFileSync(filePath, 'utf8');
    } catch (e) {
        errors.push(`Could not read file: ${e.message}`);
        return { errors, warnings };
    }

    // 1. Validate Frontmatter (YAML)
    let data, mdxContent;
    try {
        const parsed = matter(content);
        data = parsed.data;
        mdxContent = parsed.content;
    } catch (e) {
        errors.push(`Invalid YAML Frontmatter: ${e.message}`);
        return { errors, warnings }; // Cannot proceed without valid frontmatter
    }

    // Check required fields
    REQUIRED_FM_FIELDS.forEach(field => {
        if (!data[field]) {
            errors.push(`Missing required frontmatter field: "${field}"`);
        }
    });

    // Validate keywords format (should be array or comma-separated string)
    if (data.keywords) {
        if (!Array.isArray(data.keywords) && typeof data.keywords !== 'string') {
            errors.push(`"keywords" must be an array or a string`);
        }
    }

    // 2. Validate MDX Syntax
    try {
        await compile(mdxContent);
    } catch (e) {
        errors.push(`MDX Syntax Error: ${e.message}`);
    }

    // 3. Validate Content Structure

    // Check for Prediction Section
    if (!mdxContent.includes('## Predictions by Life Area')) {
        errors.push('Missing "## Predictions by Life Area" section');
    } else {
        // Check for specific prediction tags
        const missingTags = PREDICTION_TAGS.filter(tag => !mdxContent.includes(`### ${tag}`));
        if (missingTags.length > 0) {
            errors.push(`Missing ${missingTags.length} prediction tags: ${missingTags.join(', ')}`);
        }
    }

    // Check for duplicate footers (Previous/Next Article)
    const prevArticleMatches = (mdxContent.match(/## Previous Article/g) || []).length;
    const nextArticleMatches = (mdxContent.match(/## Next Article/g) || []).length;

    if (prevArticleMatches > 1) errors.push(`Found ${prevArticleMatches} "Previous Article" sections (should be 1)`);
    if (nextArticleMatches > 1) errors.push(`Found ${nextArticleMatches} "Next Article" sections (should be 1)`);

    // Check for broken internal links (basic check)
    // Looks for [Link Text](path/to/file.mdx) where file doesn't exist
    const linkRegex = /\[.*?\]\((.*?\.mdx)\)/g;
    let match;
    while ((match = linkRegex.exec(mdxContent)) !== null) {
        const linkPath = match[1];
        // Resolve path relative to current file
        const absoluteLinkPath = path.resolve(path.dirname(filePath), linkPath);

        // Handle /blogs-md/ alias
        // Based on existing files, /blogs-md/ seems to map to 06_Planet_in_Houses/ or similar
        // We'll try to resolve it by prepending 06_Planet_in_Houses if it's missing
        let projectRootLinkPath;
        if (linkPath.startsWith('/blogs-md/')) {
            const relativePath = linkPath.replace('/blogs-md/', '06_Planet_in_Houses/');
            projectRootLinkPath = path.join(process.cwd(), relativePath);
        } else if (linkPath.startsWith('/')) {
            projectRootLinkPath = path.join(process.cwd(), linkPath);
        } else {
            projectRootLinkPath = absoluteLinkPath;
        }

        if (!fs.existsSync(absoluteLinkPath) && !fs.existsSync(projectRootLinkPath)) {
            // Debug: print what we tried
            // console.log(`Failed to find: ${projectRootLinkPath}`);
            warnings.push(`Potential broken link: ${linkPath} (Resolved: ${projectRootLinkPath})`);
        }
    }

    return { errors, warnings };
}

async function run() {
    console.log(chalk.blue.bold(`\n🚀 Starting Advanced Validation for: ${TARGET_DIR}\n`));

    const projectRoot = path.join(__dirname, '..');
    const pattern = path.join(TARGET_DIR, '*.mdx');
    const files = glob.sync(pattern, { cwd: projectRoot, absolute: true });

    let totalErrors = 0;
    let filesWithErrors = 0;
    let processedCount = 0;

    for (const file of files) {
        processedCount++;
        const { errors, warnings } = await validateFile(file);

        if (errors.length > 0 || warnings.length > 0) {
            console.log(chalk.white.bold(`📄 ${path.basename(file)}`));

            if (errors.length > 0) {
                filesWithErrors++;
                totalErrors += errors.length;
                errors.forEach(err => console.log(chalk.red(`   ❌ ${err}`)));
            }

            if (warnings.length > 0) {
                warnings.forEach(warn => console.log(chalk.yellow(`   ⚠️  ${warn}`)));
            }
            console.log(''); // Empty line
        } else {
            // Optional: verbose success
            // console.log(chalk.green(`   ✅ Valid`));
        }
    }

    console.log(chalk.gray('---------------------------------------------------'));
    if (filesWithErrors > 0) {
        console.log(chalk.red.bold(`\n💥 Validation Failed!`));
        console.log(chalk.red(`   ${filesWithErrors} files have errors.`));
        console.log(chalk.red(`   ${totalErrors} total errors found.`));
        process.exit(1);
    } else {
        console.log(chalk.green.bold(`\n✨ Validation Passed!`));
        console.log(chalk.green(`   ${processedCount} files checked. No errors found.`));
        process.exit(0);
    }
}

run().catch(err => {
    console.error(chalk.red('Fatal Script Error:'), err);
    process.exit(1);
});
