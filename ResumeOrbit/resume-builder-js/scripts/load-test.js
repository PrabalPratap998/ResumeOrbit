const autocannon = require('autocannon');

function runAutocannon(config) {
  return new Promise((resolve, reject) => {
    const instance = autocannon(config, (err, result) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(result);
    });

    autocannon.track(instance, { renderProgressBar: true });
  });
}

function formatSummary(name, result) {
  return {
    test: name,
    avgLatencyMs: Number(result.latency?.average || 0).toFixed(2),
    p99LatencyMs: Number(result.latency?.p99 || 0).toFixed(2),
    reqPerSec: Number(result.requests?.average || 0).toFixed(2),
    throughputMbSec: (Number(result.throughput?.average || 0) / (1024 * 1024)).toFixed(2),
    non2xx: result.non2xx || 0,
    errors: result.errors || 0,
    timeouts: result.timeouts || 0
  };
}

async function main() {
  const tests = [
    {
      name: 'node_health_medium',
      config: {
        url: 'http://localhost:3001/api/health',
        connections: 60,
        pipelining: 10,
        duration: 30,
        method: 'GET'
      }
    },
    {
      name: 'python_parse_text_medium',
      config: {
        url: 'http://localhost:5000/parse/text',
        connections: 20,
        duration: 30,
        method: 'POST',
        headers: {
          'content-type': 'application/json'
        },
        body: JSON.stringify({
          resume_text:
            'John Doe\nSenior Python Developer\nSkills: Python, JavaScript, SQL, Flask, Docker, AWS\nExperience: Built APIs and web apps for enterprise clients.'
        })
      }
    }
  ];

  const summaries = [];

  for (const test of tests) {
    console.log(`\n--- Running ${test.name} ---`);
    const result = await runAutocannon(test.config);
    summaries.push(formatSummary(test.name, result));
  }

  console.log('\n=== Medium Traffic Summary ===');
  console.table(summaries);

  const hasFailures = summaries.some((row) => Number(row.non2xx) > 0 || Number(row.errors) > 0 || Number(row.timeouts) > 0);

  if (hasFailures) {
    console.error('\nLoad test finished with failures.');
    process.exit(1);
  }

  console.log('\nLoad test finished successfully.');
}

main().catch((err) => {
  console.error('Load test failed to run:', err);
  process.exit(1);
});
