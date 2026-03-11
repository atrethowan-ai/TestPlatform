import { readFileSync } from 'fs';
import { QuizSchema } from '@shared_types/src/schemas/quizSchema';

export function validateQuiz(file: string) {
  const raw = readFileSync(file, 'utf-8');
  const json = JSON.parse(raw);
  try {
    QuizSchema.parse(json);
    console.log('Quiz is valid!');
  } catch (e) {
    console.error('Validation failed:', e);
    process.exit(1);
  }
}
