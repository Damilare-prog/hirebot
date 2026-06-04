import { JobScraper } from './scraper.js';

async function main() {
  const scraper = new JobScraper();
  await scraper.init();

  try {
    console.log('Starting job scrape...');

    // Scrape multiple sources
    const greenhouseJobs = await scraper.scrapeGreenhouse('stripe');
    const remoteJobs = await scraper.scrapeRemoteCo();

    const allJobs = [...greenhouseJobs, ...remoteJobs];
    console.log(`Found ${allJobs.length} jobs`);

    if (allJobs.length > 0) {
      const result = await scraper.pushToAPI(allJobs);
      console.log('Push result:', result);
    }
  } finally {
    await scraper.close();
  }
}

main().catch(console.error);
