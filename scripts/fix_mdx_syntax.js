const fs = require('fs');
const path = require('path');
const glob = require('glob');
const chalk = require('chalk');

const MDX_PATTERN = '**/*.mdx';
const IGNORE_PATTERN = ['node_modules/**', 'README.md'];

function fixFile(filePath) {
    try {
        let content = fs.readFileSync(filePath, 'utf8');
        const originalContent = content;

        // Replace ## Title {#id} with <h2 id="id">Title</h2>
        // Regex to capture level, title, and id
        // Handles h1 to h6
        content = content.replace(/^(#{1,6})\s+(.*?)\s+\{#([a-zA-Z0-9-]+)\}$/gm, (match, hashes, title, id) => {
            const level = hashes.length;
            return `<h${level} id="${id}">${title}</h${level}>`;
        });

        if (content !== originalContent) {
            fs.writeFileSync(filePath, content, 'utf8');
            return true;
        }
    } catch (err) {
        console.error(chalk.red(`Error processing ${filePath}:`), err.message);
    }
    return false;
}

function run() {
    console.log(chalk.blue('Starting MDX Syntax Auto-Fix...'));

    const projectRoot = path.join(__dirname, '..');
    const files = glob.sync(MDX_PATTERN, { cwd: projectRoot, ignore: IGNORE_PATTERN, absolute: true });
    let fixedCount = 0;

    for (const file of files) {
        if (fixFile(file)) {
            fixedCount++;
            process.stdout.write(chalk.green('.'));
        } else {
            process.stdout.write(chalk.gray('.'));
        }
    }

    console.log(chalk.blue(`\n\nFixed ${fixedCount} files.`));
    console.log(chalk.green('Syntax fix completed. Run validation to verify.'));
}

run();
