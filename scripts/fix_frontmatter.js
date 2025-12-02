const fs = require('fs');
const path = require('path');
const glob = require('glob');
const matter = require('gray-matter');
const chalk = require('chalk');

const MDX_PATTERN = '**/*.mdx';
const IGNORE_PATTERN = ['node_modules/**', 'README.md'];

function generateKeywords(title, filePath) {
    const keywords = new Set();

    // Add words from title
    if (title) {
        title.split(/[\s:-]+/).forEach(word => {
            if (word.length > 3 && !['with', 'from', 'into', 'your', 'what', 'this', 'that'].includes(word.toLowerCase())) {
                keywords.add(word.trim());
            }
        });
    }

    // Add directory context
    const dirName = path.dirname(filePath).split(path.sep).pop();
    if (dirName && dirName !== '.') {
        keywords.add(dirName.replace(/_/g, ' '));
    }

    // Add generic tags
    keywords.add('Vedic Astrology');
    keywords.add('Astrology');

    return Array.from(keywords);
}

function generateDescription(title) {
    return `Comprehensive guide on ${title}. Learn about its significance, effects, and remedies in Vedic Astrology.`;
}

async function fixFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const file = matter(content);
        let changed = false;

        // Fix Title (if missing, though unlikely for valid files)
        if (!file.data.title) {
            // Fallback to filename if title is absolutely missing
            const basename = path.basename(filePath, '.mdx');
            file.data.title = basename.replace(/_/g, ' ');
            changed = true;
        }

        // Fix Keywords
        if (!file.data.keywords || (Array.isArray(file.data.keywords) && file.data.keywords.length === 0)) {
            file.data.keywords = generateKeywords(file.data.title, filePath);
            changed = true;
        }

        // Fix Description
        if (!file.data.description) {
            file.data.description = generateDescription(file.data.title);
            changed = true;
        }

        if (changed) {
            const newContent = matter.stringify(file.content, file.data);
            fs.writeFileSync(filePath, newContent, 'utf8');
            return true;
        }
    } catch (err) {
        console.error(chalk.red(`Error processing ${filePath}:`), err.message);
    }
    return false;
}

async function run() {
    console.log(chalk.blue('Starting Frontmatter Auto-Fix...'));

    const projectRoot = path.join(__dirname, '..');
    const files = glob.sync(MDX_PATTERN, { cwd: projectRoot, ignore: IGNORE_PATTERN, absolute: true });
    let fixedCount = 0;

    for (const file of files) {
        const wasFixed = await fixFile(file);
        if (wasFixed) {
            fixedCount++;
            process.stdout.write(chalk.green('.'));
        } else {
            process.stdout.write(chalk.gray('.'));
        }
    }

    console.log(chalk.blue(`\n\nFixed ${fixedCount} files.`));
    console.log(chalk.green('Auto-fix completed. Run validation to verify.'));
}

run();
