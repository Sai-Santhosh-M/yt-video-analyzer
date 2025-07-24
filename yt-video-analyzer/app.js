const express = require('express');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Set view engine and views
app.set('view engine', 'ejs');
app.set('views', __dirname);
app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.urlencoded({ extended: true }));

// GET home page
app.get('/', (req, res) => {
  res.render('index', { sentimentData: null, comments: [], summary: null });
});

// POST to analyze
app.post('/', (req, res) => {
  const videoUrl = req.body.videoUrl;
  console.log("🎥 Received URL:", videoUrl);

  // Step 1: Fetch comments
  exec(`python youtube.py "${videoUrl}"`, (error1, stdout1, stderr1) => {
    if (error1) {
      console.error("❌ Error fetching comments:", stderr1);
      return res.send(`❌ Error fetching comments: ${stderr1}`);
    }

    // Step 2: Analyze comments
    exec('python analysis.py', (error2, stdout2, stderr2) => {
      if (error2) {
        console.error("❌ Error analyzing comments:", stderr2);
        return res.send(`❌ Error analyzing comments: ${stderr2}`);
      }

      // Step 3: Get transcript and short summary
      exec(`python transcript.py "${videoUrl}"`, (error3, stdout3, stderr3) => {
        if (error3) {
          console.error("❌ Error getting transcript/summary:", stderr3);
          return res.send(`❌ Error getting transcript/summary: ${stderr3}`);
        }

        // Load data
        let sentimentData = null;
        let comments = [];
        let summary = null;

        try {
          // Sentiment analysis data
          const raw = fs.readFileSync(path.join(__dirname, 'results.json'), 'utf-8');
          const parsed = JSON.parse(raw);
          sentimentData = {
            total: parsed.total,
            positive: parsed.positive_percent,
            neutral: ((parsed.neutral / parsed.total) * 100).toFixed(1),
            negative: ((parsed.negative / parsed.total) * 100).toFixed(1)
          };
          comments = parsed.details;

          // Summary data
          const summaryRaw = fs.readFileSync(path.join(__dirname, 'summary.json'), 'utf-8');
          const summaryParsed = JSON.parse(summaryRaw);
          summary = summaryParsed.summary;

        } catch (err) {
          console.error("❌ Error reading JSON files:", err);
        }

        // Render page
        res.render('index', { sentimentData, comments, summary });
      });
    });
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
