// API Endpoint - 環境に応じて自動切替
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'  // ローカル開発環境
    : 'https://x-bot-analyzer.onrender.com';  // 本番環境（Render）

let currentAnalysis = null;

async function analyzeAccount() {
    const accountUrl = document.getElementById('accountUrl').value.trim();

    if (!accountUrl) {
        showError('アカウントURLを入力してください');
        return;
    }

    // URL validation
    if (!isValidTwitterUrl(accountUrl)) {
        showError('有効なX（Twitter）のアカウントURLを入力してください\n例: https://x.com/username または https://twitter.com/username');
        return;
    }

    // Show loading
    showLoading();

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: accountUrl })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '分析に失敗しました');
        }

        const data = await response.json();
        currentAnalysis = data;
        showResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'サーバーとの通信に失敗しました。バックエンドが起動しているか確認してください。');
    }
}

function isValidTwitterUrl(url) {
    const patterns = [
        /^https?:\/\/(www\.)?(twitter\.com|x\.com)\/[a-zA-Z0-9_]+\/?$/,
        /^https?:\/\/(www\.)?(twitter\.com|x\.com)\/[a-zA-Z0-9_]+$/
    ];
    return patterns.some(pattern => pattern.test(url));
}

function showLoading() {
    document.querySelector('.input-section').classList.add('hidden');
    document.getElementById('resultSection').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');
    document.getElementById('loadingSection').classList.remove('hidden');

    // Simulate progress steps
    setTimeout(() => document.getElementById('step1').classList.add('active'), 500);
    setTimeout(() => document.getElementById('step2').classList.add('active'), 3000);
    setTimeout(() => document.getElementById('step3').classList.add('active'), 6000);
}

function showResults(data) {
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('resultSection').classList.remove('hidden');

    // Account info
    if (data.account) {
        document.getElementById('accountName').textContent = data.account.name || 'Unknown';
        document.getElementById('accountHandle').textContent = '@' + (data.account.username || 'unknown');
        document.getElementById('accountIcon').src = data.account.profile_image || 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';
    }

    // Overall score
    const humanScore = Math.round(data.analysis.overall_score);
    document.getElementById('humanScore').textContent = humanScore + '%';

    // Animate circle
    const circle = document.getElementById('scoreCircle');
    const circumference = 565.48;
    const offset = circumference - (humanScore / 100) * circumference;
    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
    }, 100);

    // Set circle color based on score
    if (humanScore >= 70) {
        circle.style.stroke = '#17BF63';
    } else if (humanScore >= 40) {
        circle.style.stroke = '#FFAD1F';
    } else {
        circle.style.stroke = '#E0245E';
    }

    // Verdict
    const verdict = getVerdict(humanScore);
    document.getElementById('verdictIcon').textContent = verdict.icon;
    document.getElementById('verdictText').textContent = verdict.text;
    document.getElementById('verdictText').style.color = verdict.color;

    // Detail scores
    const scores = data.analysis.detailed_scores;
    setDetailScore('patternScore', scores.posting_pattern, data.analysis.details.posting_pattern);
    setDetailScore('textScore', scores.text_naturalness, data.analysis.details.text_naturalness);
    setDetailScore('commScore', scores.communication, data.analysis.details.communication);
    setDetailScore('emotionScore', scores.emotion_expression, data.analysis.details.emotion_expression);

    // AI Summary
    document.getElementById('aiSummary').textContent = data.analysis.ai_summary;

    // Tweet samples
    displayTweetSamples(data.tweets);
}

function setDetailScore(elementId, score, description) {
    const scoreElement = document.getElementById(elementId);
    const descElement = document.getElementById(elementId.replace('Score', 'Analysis'));

    setTimeout(() => {
        scoreElement.style.width = score + '%';
    }, 100);

    if (descElement) {
        descElement.textContent = description;
    }
}

function getVerdict(score) {
    if (score >= 80) {
        return {
            icon: '👤',
            text: 'ほぼ確実に人間です',
            color: '#17BF63'
        };
    } else if (score >= 60) {
        return {
            icon: '🤔',
            text: '人間の可能性が高い',
            color: '#17BF63'
        };
    } else if (score >= 40) {
        return {
            icon: '⚠️',
            text: '判定が難しいです',
            color: '#FFAD1F'
        };
    } else if (score >= 20) {
        return {
            icon: '🤖',
            text: 'BOTの可能性が高い',
            color: '#E0245E'
        };
    } else {
        return {
            icon: '🤖',
            text: 'ほぼ確実にBOTです',
            color: '#E0245E'
        };
    }
}

function displayTweetSamples(tweets) {
    const tweetList = document.getElementById('tweetList');
    tweetList.innerHTML = '';

    const samplesToShow = tweets.slice(0, 5);

    samplesToShow.forEach(tweet => {
        const tweetDiv = document.createElement('div');
        tweetDiv.className = 'tweet-item';

        const dateDiv = document.createElement('div');
        dateDiv.className = 'tweet-date';
        dateDiv.textContent = formatDate(tweet.date);

        const textDiv = document.createElement('div');
        textDiv.className = 'tweet-text';
        textDiv.textContent = tweet.text;

        tweetDiv.appendChild(dateDiv);
        tweetDiv.appendChild(textDiv);
        tweetList.appendChild(tweetDiv);
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showError(message) {
    document.querySelector('.input-section').classList.add('hidden');
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('resultSection').classList.add('hidden');
    document.getElementById('errorSection').classList.remove('hidden');

    document.getElementById('errorMessage').textContent = message;
}

function resetAnalysis() {
    document.querySelector('.input-section').classList.remove('hidden');
    document.getElementById('loadingSection').classList.add('hidden');
    document.getElementById('resultSection').classList.add('hidden');
    document.getElementById('errorSection').classList.add('hidden');

    document.getElementById('accountUrl').value = '';
    currentAnalysis = null;

    // Reset progress steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
}

// Allow Enter key to submit
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('accountUrl').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeAccount();
        }
    });
});
