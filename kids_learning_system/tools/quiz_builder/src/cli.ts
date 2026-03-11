#!/usr/bin/env node
import { validateQuiz } from './commands/validateQuiz';

const [,, cmd, ...args] = process.argv;

if (cmd === 'validate') {
  validateQuiz(args[0]);
} else {
  console.log('quiz-builder <command>');
  console.log('Commands: validate <file>');
}
