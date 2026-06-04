import { AutoApplyEngine } from './scraper.js';

async function main() {
  const engine = new AutoApplyEngine();
  await engine.init();

  try {
    // In production: read from Redis queue / API
    const testUrl = process.argv[2];
    const formData = JSON.parse(process.argv[3] || '{}');

    if (!testUrl) {
      console.log('Usage: npm run apply -- <url> '<form_data_json>'');
      process.exit(1);
    }

    const result = await engine.applyToGreenhouse(testUrl, formData);
    console.log('Apply result:', result);
  } finally {
    await engine.close();
  }
}

main().catch(console.error);
