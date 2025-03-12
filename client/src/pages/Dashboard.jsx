import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Clock, TrendingUp, Hash, MessageSquare, BarChart2, AlertTriangle } from 'lucide-react';

const SocialMediaDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [countdown, setCountdown] = useState(35 * 60); // 35 minutes in seconds

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // In a real app, this would be your API endpoint
        const response = await fetch('http://localhost:5000/api/trends');
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        const jsonData = await response.json();
        setData(jsonData); // Set the whole response as data
        setLastUpdated(new Date());
        setCountdown(35 * 60); // Reset countdown
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // For demo purposes, let's use the sample data
    const sampleData = {
      "_id": "67d1e601339d0d4ab59040de",
      "ai_analysis": {
        "content_recommendations": [
          "Create short, engaging videos explaining blockchain basics and showcasing real-world applications.",
          "Develop content that bridges the gap between futuristic concepts (Metaverse, AI) and practical implementations using blockchain.",
          "Focus on educational content targeted at beginners interested in cryptocurrency and blockchain technology. Explain the technology in a simple and easy to understand manner.",
          "Highlight the benefits of blockchain technology across various industries and its impact on everyday life.",
          "Partner with technology influencers and experts to create credible and trustworthy content.",
          "Encourage user interaction and feedback to gauge sentiment and address concerns regarding blockchain technology."
        ],
        "emerging_patterns": [
          "Convergence of blockchain technology with diverse sectors (automotive, holograms, manufacturing).",
          "Emphasis on accessibility and ease of understanding of cryptocurrency concepts (e.g. #cryptoforbeginners).",
          "Utilization of short-form video for quick technology updates and science demonstrations.",
          "Focus on practical applications and tangible benefits of blockchain rather than purely speculative or investment-oriented narratives.",
          "Trend of blockchain startups showcasing their technological innovations through various channels (Reddit, Youtube, Bluesky)."
        ],
        "key_insights": [
          "Short-form video content (shorts) is a dominant medium for disseminating information and engaging with audiences across technology, science, and crypto topics.",
          "While blockchain and cryptocurrency remain key themes, there's a visible effort to broaden the appeal by connecting them to tangible applications like car seat technology and Industry 4.0 solutions (Swisstronik).",
          "The integration of blockchain technology with diverse fields like hologram development and public recognition algorithms suggests a trend towards real-world utility beyond finance.",
          "There is also a strong element of basic or intro-level crypto education and discussion happening, evidenced by hashtags like #cryptoforbeginners and keywords like 'crypto'.",
          "The data highlights a mix of futuristic aspirations (Metaverse_Blockchain, 'This is future...') and practical advancements (carseat technology, Swisstronik).",
          "There is a potential disconnect between the neutral sentiment and the focus on 'revolutionary' and 'future' technologies. Sentiment may be cautiously optimistic or hesitant."
        ],
        "sentiment_analysis": "The overall sentiment is neutral, which is interesting considering the presence of terms like 'revolutionary' and 'future'. This might indicate a cautious optimism or a wait-and-see approach from the audience. It could also reflect a skepticism towards overly hyped technologies, or a deliberate attempt by content creators to avoid overly positive pronouncements that might be perceived as shilling or biased. Further investigation into user comments and engagement is needed to understand the nuances of this neutral sentiment.",
        "summary": "The data indicates a burgeoning interest in blockchain technology's practical applications across diverse sectors, driven by short-form video content and educational initiatives aimed at beginners. While sentiment remains neutral, there is potential for increased engagement as the technology becomes more accessible and its real-world benefits become clearer.",
        "timestamp": "2025-03-12T19:52:33.099360",
        "trend_prediction": "In the next 24-48 hours, expect to see a continued focus on short-form video content explaining blockchain applications across various industries. There will likely be a surge in content targeted at beginners, aiming to demystify cryptocurrency and blockchain concepts. The sentiment is likely to remain neutral, possibly with a slight lean towards positive as more practical applications are showcased. We anticipate more startups leveraging these channels to showcase cutting-edge innovations."
      },
      "domain": "technology,Blockchain",
      "sentiment": {
        "data": {
          "textblob": {
            "avg_polarity": 0.07461771473444469,
            "avg_subjectivity": 0.33921012175891246
          },
          "transformer": {
            "avg_confidence": 0.9012164858079725,
            "positive_percentage": 43.07692307692308
          }
        },
        "overall_mood": "neutral"
      },
      "timestamp": "2025-03-12T19:52:19.406000",
      "top_hashtags": {
        "45": 2,
        "50Cent": 1,
        "7": 1,
        "AyoTechnology": 1,
        "BTC": 2,
        "Blockchain": 2,
        "CryptoEducation": 2,
        "CryptoExplained": 2,
        "CryptoInvesting": 2,
        "CryptoMarket": 2,
        "CryptoStaking": 2,
        "CryptoTrading": 2,
        "JustinTimberlake": 1,
        "Remastered": 1,
        "bitcoin": 3,
        "blockchain": 2,
        "blum": 3,
        "blumacademy": 3,
        "crypto": 3,
        "cryptocurrency": 3,
        "cryptoforbeginners": 3,
        "insideout2": 1,
        "science": 4,
        "shorts": 7,
        "tech": 3,
        "technology": 6,
        "trending": 4,
        "virtualreality": 1,
        "visor": 1,
        "vr": 1
      },
      "top_trends": [
        "CryptoTechnology",
        "blockchain_startups",
        "CryptoCurrency",
        "Bitcoin",
        "Metaverse_Blockchain",
        "50 Cent -...",
        "This is future...",
        "Worlds smallest 4K...",
        "New Science Project...",
        "Revolutionary carseat technology..."
      ],
      "top_words": {
        "bitcoin": 12,
        "blockchain": 27,
        "crypto": 17,
        "like": 13,
        "mini": 13,
        "project": 15,
        "science": 13,
        "technology": 35,
        "tractor": 27,
        "video": 20
      }
    };
    
    setData(sampleData);
    setLoading(false);

    // Set up auto-refresh every 35 minutes
    const refreshInterval = setInterval(fetchData, 35 * 60 * 1000);

    // Countdown timer
    const countdownInterval = setInterval(() => {
      setCountdown(prevCountdown => {
        if (prevCountdown <= 1) return 35 * 60; // Reset when it hits zero
        return prevCountdown - 1;
      });
    }, 1000);

    return () => {
      clearInterval(refreshInterval);
      clearInterval(countdownInterval);
    };
  }, []);

  const formatCountdown = () => {
    const minutes = Math.floor(countdown / 60);
    const seconds = countdown % 60;
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  // Function to prepare hashtag data for chart
  const prepareHashtagsData = () => {
    if (!data || !data.top_hashtags) return [];
    
    return Object.entries(data.top_hashtags)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([tag, count]) => ({ name: `#${tag}`, count }));
  };

  // Function to prepare words data for chart
  const prepareWordsData = () => {
    if (!data || !data.top_words) return [];
    
    return Object.entries(data.top_words)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([word, count]) => ({ name: word, count }));
  };

  // Function to get sentiment color
  const getSentimentColor = () => {
    if (!data || !data.sentiment || !data.sentiment.overall_mood) return 'text-gray-500';
    
    switch (data.sentiment.overall_mood.toLowerCase()) {
      case 'positive':
        return 'text-green-500';
      case 'negative':
        return 'text-red-500';
      default:
        return 'text-yellow-500'; // neutral
    }
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-purple-400 text-xl">Loading dashboard data...</div>
      </div>
    );
  }

  // Handle error state
  if (error && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 p-8">
        <AlertTriangle size={48} className="text-red-500 mb-4" />
        <h1 className="text-2xl text-red-400 mb-2">Error Loading Dashboard</h1>
        <p className="text-gray-300 mb-4">{error}</p>
        <button 
          className="px-4 py-2 bg-purple-700 text-white rounded-md hover:bg-purple-600"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-2">
            <h1 className="text-3xl font-bold text-purple-400 mb-2 sm:mb-0">Social Media Trends Dashboard</h1>
            <div className="flex items-center text-sm">
              <Clock size={16} className="mr-2 text-purple-400" />
              <span className="mr-4">Next refresh in: {formatCountdown()}</span>
              <span className="text-gray-400">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </span>
            </div>
          </div>
          <div className="flex flex-wrap items-center text-sm text-gray-400">
            <span className="mr-6">
              Domain: {data?.domain || 'N/A'}
            </span>
            <span className="mr-6">
              Date: {data?.timestamp ? new Date(data.timestamp).toLocaleDateString() : 'N/A'}
            </span>
            <span className="flex items-center">
              Sentiment: 
              <span className={`ml-2 font-medium ${getSentimentColor()}`}>
                {data?.sentiment?.overall_mood ? 
                  data.sentiment.overall_mood.charAt(0).toUpperCase() + data.sentiment.overall_mood.slice(1) : 
                  'Unknown'
                }
              </span>
            </span>
          </div>
        </header>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Trends Card */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-purple-800">
            <div className="flex items-center mb-4">
              <TrendingUp size={20} className="text-purple-500 mr-2" />
              <h2 className="text-xl font-semibold">Top Trends</h2>
            </div>
            {data?.top_trends && data.top_trends.length > 0 ? (
              <ul className="space-y-3">
                {data.top_trends.map((trend, index) => (
                  <li key={index} className="flex items-start">
                    <span className="bg-purple-900 text-purple-200 w-7 h-7 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                      {index + 1}
                    </span>
                    <span className="text-gray-200">{trend}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-gray-400 py-8 text-center">No trend data available</div>
            )}
          </div>

          {/* Top Hashtags Chart */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-purple-800">
            <div className="flex items-center mb-4">
              <Hash size={20} className="text-purple-500 mr-2" />
              <h2 className="text-xl font-semibold">Top Hashtags</h2>
            </div>
            {data?.top_hashtags && Object.keys(data.top_hashtags).length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={prepareHashtagsData()} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis type="number" stroke="#aaa" />
                    <YAxis dataKey="name" type="category" width={80} stroke="#aaa" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '4px' }}
                      itemStyle={{ color: '#e5e7eb' }}
                      labelStyle={{ color: '#a78bfa' }}
                    />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="text-gray-400 py-8 text-center h-64 flex items-center justify-center">
                No hashtag data available
              </div>
            )}
          </div>

          {/* Top Words Chart */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-purple-800">
            <div className="flex items-center mb-4">
              <MessageSquare size={20} className="text-purple-500 mr-2" />
              <h2 className="text-xl font-semibold">Top Words</h2>
            </div>
            {data?.top_words && Object.keys(data.top_words).length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={prepareWordsData()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis dataKey="name" stroke="#aaa" />
                    <YAxis stroke="#aaa" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '4px' }}
                      itemStyle={{ color: '#e5e7eb' }}
                      labelStyle={{ color: '#a78bfa' }}
                    />
                    <Bar dataKey="count" fill="#a78bfa" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="text-gray-400 py-8 text-center h-64 flex items-center justify-center">
                No word data available
              </div>
            )}
          </div>

          {/* AI Insights Card */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-purple-800">
            <div className="flex items-center mb-4">
              <BarChart2 size={20} className="text-purple-500 mr-2" />
              <h2 className="text-xl font-semibold">AI Insights</h2>
            </div>
            {data?.ai_analysis ? (
              <div className="space-y-4 overflow-y-auto max-h-64">
                <div>
                  <h3 className="text-purple-400 font-medium mb-2">Key Insights</h3>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {data.ai_analysis.key_insights?.slice(0, 3).map((insight, index) => (
                      <li key={index} className="text-gray-300">{insight}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-purple-400 font-medium mb-2">Emerging Patterns</h3>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {data.ai_analysis.emerging_patterns?.slice(0, 2).map((pattern, index) => (
                      <li key={index} className="text-gray-300">{pattern}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-purple-400 font-medium mb-2">Prediction</h3>
                  <p className="text-gray-300 text-sm">
                    {data.ai_analysis.trend_prediction?.slice(0, 150)}
                    {data.ai_analysis.trend_prediction?.length > 150 ? '...' : ''}
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-gray-400 py-8 text-center">No AI analysis available</div>
            )}
          </div>
        </div>

        {/* Content Recommendations */}
        <div className="mt-6 bg-gray-800 rounded-lg shadow-lg p-6 border border-purple-800">
          <div className="flex items-center mb-4">
            <TrendingUp size={20} className="text-purple-500 mr-2" />
            <h2 className="text-xl font-semibold">Content Recommendations</h2>
          </div>
          {data?.ai_analysis?.content_recommendations && data.ai_analysis.content_recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.ai_analysis.content_recommendations.map((recommendation, index) => (
                <div key={index} className="bg-gray-700 p-4 rounded-md border-l-4 border-purple-500">
                  <p className="text-gray-200 text-sm">{recommendation}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-400 py-4 text-center">No content recommendations available</div>
          )}
        </div>

        {/* Sentiment Details */}
        <div className="mt-6 bg-gray-800 rounded-lg shadow-lg p-6 border border-purple-800">
          <div className="flex items-center mb-4">
            <BarChart2 size={20} className="text-purple-500 mr-2" />
            <h2 className="text-xl font-semibold">Sentiment Analysis</h2>
          </div>
          {data?.sentiment?.data ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-700 p-4 rounded-md">
                <h3 className="text-purple-400 font-medium mb-2">TextBlob Analysis</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Polarity:</span>
                    <span className="text-gray-200 font-medium">
                      {data.sentiment.data.textblob?.avg_polarity?.toFixed(3) || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Subjectivity:</span>
                    <span className="text-gray-200 font-medium">
                      {data.sentiment.data.textblob?.avg_subjectivity?.toFixed(3) || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-700 p-4 rounded-md">
                <h3 className="text-purple-400 font-medium mb-2">Transformer Analysis</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-300">Positive %:</span>
                    <span className="text-gray-200 font-medium">
                      {data.sentiment.data.transformer?.positive_percentage?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Confidence:</span>
                    <span className="text-gray-200 font-medium">
                      {data.sentiment.data.transformer?.avg_confidence?.toFixed(3)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="md:col-span-2">
                <h3 className="text-purple-400 font-medium mb-2">Expert Analysis</h3>
                <p className="text-gray-300 text-sm">
                  {data.ai_analysis?.sentiment_analysis || 'No sentiment analysis available'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-gray-400 py-4 text-center">No sentiment data available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialMediaDashboard;