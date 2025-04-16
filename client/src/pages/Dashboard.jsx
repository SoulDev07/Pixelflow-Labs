import React, { useState, useEffect } from "react";
import { Clock, AlertTriangle, Zap, Sparkles, ArrowUp, ArrowDown, TrendingUp, Database } from "lucide-react";
import { motion } from "framer-motion";

import Chart from "react-apexcharts";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

const SocialMediaDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [countdown, setCountdown] = useState(35 * 60); // 35 minutes in seconds
  const [themeColor, setThemeColor] = useState("purple");

  // Sample data to use when API fails
  const sampleData = {
    _id: "67d1e601339d0d4ab59040de",
    ai_analysis: {
      content_recommendations: [
        "Create short, engaging videos explaining blockchain basics and showcasing real-world applications.",
        "Develop content that bridges the gap between futuristic concepts (Metaverse, AI) and practical implementations using blockchain.",
        "Focus on educational content targeted at beginners interested in cryptocurrency and blockchain technology. Explain the technology in a simple and easy to understand manner.",
        "Highlight the benefits of blockchain technology across various industries and its impact on everyday life.",
        "Partner with technology influencers and experts to create credible and trustworthy content.",
        "Encourage user interaction and feedback to gauge sentiment and address concerns regarding blockchain technology.",
      ],
      emerging_patterns: [
        "Convergence of blockchain technology with diverse sectors (automotive, holograms, manufacturing).",
        "Emphasis on accessibility and ease of understanding of cryptocurrency concepts (e.g. #cryptoforbeginners).",
        "Utilization of short-form video for quick technology updates and science demonstrations.",
        "Focus on practical applications and tangible benefits of blockchain rather than purely speculative or investment-oriented narratives.",
        "Trend of blockchain startups showcasing their technological innovations through various channels (Reddit, Youtube, Bluesky).",
      ],
      key_insights: [
        "Short-form video content (shorts) is a dominant medium for disseminating information and engaging with audiences across technology, science, and crypto topics.",
        "While blockchain and cryptocurrency remain key themes, there's a visible effort to broaden the appeal by connecting them to tangible applications like car seat technology and Industry 4.0 solutions (Swisstronik).",
        "The integration of blockchain technology with diverse fields like hologram development and public recognition algorithms suggests a trend towards real-world utility beyond finance.",
        "There is also a strong element of basic or intro-level crypto education and discussion happening, evidenced by hashtags like #cryptoforbeginners and keywords like 'crypto'.",
        "The data highlights a mix of futuristic aspirations (Metaverse_Blockchain, 'This is future...') and practical advancements (carseat technology, Swisstronik).",
        "There is a potential disconnect between the neutral sentiment and the focus on 'revolutionary' and 'future' technologies. Sentiment may be cautiously optimistic or hesitant.",
      ],
      sentiment_analysis:
        "The overall sentiment is neutral, which is interesting considering the presence of terms like 'revolutionary' and 'future'. This might indicate a cautious optimism or a wait-and-see approach from the audience. It could also reflect a skepticism towards overly hyped technologies, or a deliberate attempt by content creators to avoid overly positive pronouncements that might be perceived as shilling or biased. Further investigation into user comments and engagement is needed to understand the nuances of this neutral sentiment.",
      summary:
        "The data indicates a burgeoning interest in blockchain technology's practical applications across diverse sectors, driven by short-form video content and educational initiatives aimed at beginners. While sentiment remains neutral, there is potential for increased engagement as the technology becomes more accessible and its real-world benefits become clearer.",
      timestamp: "2025-03-12T19:52:33.099360",
      trend_prediction:
        "In the next 24-48 hours, expect to see a continued focus on short-form video content explaining blockchain applications across various industries. There will likely be a surge in content targeted at beginners, aiming to demystify cryptocurrency and blockchain concepts. The sentiment is likely to remain neutral, possibly with a slight lean towards positive as more practical applications are showcased. We anticipate more startups leveraging these channels to showcase cutting-edge innovations.",
    },
    domain: "technology,Blockchain",
    sentiment: {
      data: {
        textblob: {
          avg_polarity: 0.07461771473444469,
          avg_subjectivity: 0.33921012175891246,
        },
        transformer: {
          avg_confidence: 0.9012164858079725,
          positive_percentage: 43.07692307692308,
        },
      },
      overall_mood: "neutral",
    },
    timestamp: "2025-03-12T19:52:19.406000",
    top_hashtags: {
      45: 2,
      "50Cent": 1,
      7: 1,
      AyoTechnology: 1,
      BTC: 2,
      Blockchain: 2,
      CryptoEducation: 2,
      CryptoExplained: 2,
      CryptoInvesting: 2,
      CryptoMarket: 2,
      CryptoStaking: 2,
      CryptoTrading: 2,
      JustinTimberlake: 1,
      Remastered: 1,
      bitcoin: 3,
      blockchain: 2,
      blum: 3,
      blumacademy: 3,
      crypto: 3,
      cryptocurrency: 3,
      cryptoforbeginners: 3,
      insideout2: 1,
      science: 4,
      shorts: 7,
      tech: 3,
      technology: 6,
      trending: 4,
      virtualreality: 1,
      visor: 1,
      vr: 1,
    },
    top_trends: [
      "CryptoTechnology",
      "blockchain_startups",
      "CryptoCurrency",
      "Bitcoin",
      "Metaverse_Blockchain",
      "50 Cent -...",
      "This is future...",
      "Worlds smallest 4K...",
      "New Science Project...",
      "Revolutionary carseat technology...",
    ],
    top_words: {
      bitcoin: 12,
      blockchain: 27,
      crypto: 17,
      like: 13,
      mini: 13,
      project: 15,
      science: 13,
      technology: 35,
      tractor: 27,
      video: 20,
    },
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:5000/api/trends");

        let jsonData = null;
        if (!response.ok) {
          jsonData = sampleData;
        } else {
          jsonData = await response.json();
        }
        setData(jsonData);
        setLastUpdated(new Date());
        setCountdown(35 * 60);
        setError(null);

        if (jsonData?.sentiment?.overall_mood) {
          if (jsonData.sentiment.overall_mood === "positive") {
            setThemeColor("emerald");
          } else if (jsonData.sentiment.overall_mood === "negative") {
            setThemeColor("rose");
          } else {
            setThemeColor("purple");
          }
        }
      } catch (err) {
        setError(err.message);
        console.error("Error fetching data:", err);
        setData(sampleData);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    const refreshInterval = setInterval(fetchData, 35 * 60 * 1000);

    const countdownInterval = setInterval(() => {
      setCountdown((prevCountdown) => {
        if (prevCountdown <= 1) return 35 * 60;
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
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  const prepareHashtagsData = () => {
    if (!data || !data.top_hashtags) return [];
    return Object.entries(data.top_hashtags)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10) // Increased to show more hashtags
      .map(([tag, count]) => ({ name: `#${tag}`, count }));
  };

  const prepareWordsData = () => {
    if (!data || !data.top_words) return [];
    return Object.entries(data.top_words)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([word, count]) => ({ name: word, count }));
  };

  const prepareHashtagsChartData = () => {
    const hashtagData = prepareHashtagsData();
    return {
      categories: hashtagData.map((item) => item.name),
      values: hashtagData.map((item) => item.count),
    };
  };

  const prepareWordsChartData = () => {
    const wordsData = prepareWordsData();
    return {
      categories: wordsData.map((item) => item.name),
      values: wordsData.map((item) => item.count),
    };
  };

  const prepareSentimentGaugeData = () => {
    if (!data || !data.sentiment || !data.sentiment.data || !data.sentiment.data.transformer) return 0;
    return Math.round(data.sentiment.data.transformer.positive_percentage);
  };

  const sentimentGaugeOptions = {
    chart: {
      type: "radialBar",
      offsetY: -20,
      sparkline: {
        enabled: true,
      },
      background: "transparent",
      animations: {
        enabled: true,
        easing: "easeinout",
        speed: 800,
        dynamicAnimation: {
          enabled: true,
        },
      },
    },
    plotOptions: {
      radialBar: {
        startAngle: -90,
        endAngle: 90,
        track: {
          background: themeColor === "purple" ? "#4c1d95" : themeColor === "emerald" ? "#064e3b" : "#881337",
          strokeWidth: "97%",
          margin: 5,
          dropShadow: {
            enabled: true,
            top: 2,
            left: 0,
            blur: 4,
            opacity: 0.15,
          },
        },
        dataLabels: {
          name: {
            show: true,
            fontSize: "16px",
            color: "#fff",
            offsetY: -10,
          },
          value: {
            offsetY: -2,
            fontSize: "22px",
            color: "#fff",
            formatter: function (val) {
              return val + "%";
            },
          },
        },
        hollow: {
          size: "45%",
          background: "transparent",
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "dark",
        type: "horizontal",
        shadeIntensity: 0.5,
        gradientToColors: [themeColor === "purple" ? "#c084fc" : themeColor === "emerald" ? "#34d399" : "#fb7185"],
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 1,
        stops: [0, 100],
      },
    },
    stroke: {
      lineCap: "round",
    },
    labels: ["Positive Sentiment"],
    grid: {
      padding: {
        top: -10,
      },
    },
    states: {
      hover: {
        filter: {
          type: "none",
        },
      },
    },
    tooltip: {
      enabled: true,
      theme: "dark",
      style: {
        fontSize: "14px",
      },
      y: {
        formatter: function (value) {
          return value + "% positive sentiment";
        },
        title: {
          formatter: function () {
            return "";
          },
        },
      },
    },
  };

  const confidenceRadarOptions = {
    chart: {
      type: "radar",
      height: 350,
      background: "transparent",
      dropShadow: {
        enabled: true,
        blur: 1,
        left: 1,
        top: 1,
        opacity: 0.2,
      },
      animations: {
        enabled: true,
        easing: "easeinout",
        speed: 700,
        dynamicAnimation: {
          enabled: true,
        },
      },
      toolbar: {
        show: false,
      },
    },
    series: [
      {
        name: "Metrics",
        data: [
          data?.sentiment?.data?.transformer?.avg_confidence * 100 || 0,
          data?.sentiment?.data?.textblob?.avg_subjectivity * 100 || 0,
          data?.sentiment?.data?.textblob?.avg_polarity * 50 + 50 || 50,
        ],
      },
    ],
    colors: [themeColor === "purple" ? "#a855f7" : themeColor === "emerald" ? "#10b981" : "#f43f5e"],
    markers: {
      size: 5,
      hover: {
        size: 9,
      },
    },
    plotOptions: {
      radar: {
        polygons: {
          strokeColors: "rgba(255,255,255,0.1)",
          fill: {
            colors: ["rgba(255,255,255,0.05)", "transparent"],
          },
        },
      },
    },
    stroke: {
      width: 2,
      curve: "smooth",
    },
    fill: {
      opacity: 0.2,
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: function (val) {
          return val.toFixed(1) + "%";
        },
      },
    },
    xaxis: {
      categories: ["Confidence", "Subjectivity", "Polarity"],
      labels: {
        style: {
          colors: ["#c4c4c4", "#c4c4c4", "#c4c4c4"],
          fontSize: "14px",
        },
      },
    },
    yaxis: {
      show: false,
      tickAmount: 5,
      min: 0,
      max: 100,
    },
    grid: {
      show: false,
    },
  };

  const hashtagsChartOptions = {
    chart: {
      type: "bar",
      height: 250,
      background: "transparent",
      toolbar: {
        show: false,
      },
      fontFamily: "Inter, system-ui, sans-serif",
    },
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 6,
        barHeight: "70%",
        distributed: true,
        dataLabels: {
          position: "top",
        },
      },
    },
    colors: [
      themeColor === "purple" ? "#c084fc" : themeColor === "emerald" ? "#34d399" : "#fb7185",
      themeColor === "purple" ? "#a855f7" : themeColor === "emerald" ? "#10b981" : "#f43f5e",
      themeColor === "purple" ? "#8b5cf6" : themeColor === "emerald" ? "#059669" : "#e11d48",
      themeColor === "purple" ? "#7c3aed" : themeColor === "emerald" ? "#047857" : "#be123c",
    ],
    dataLabels: {
      enabled: true,
      offsetX: -5,
      formatter: function (val) {
        return val;
      },
      style: {
        fontSize: "12px",
        fontWeight: 600,
        colors: ["#fff"],
      },
      background: {
        enabled: false,
      },
    },
    legend: {
      show: false,
    },
    xaxis: {
      categories: prepareHashtagsChartData().categories,
      labels: {
        style: {
          colors: Array(8).fill("#c4c4c4"),
          fontSize: "12px",
          fontWeight: 400,
        },
        formatter: function (val) {
          if (val.length > 15) {
            return val.substring(0, 12) + '...';
          }
          return val;
        },
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: Array(8).fill("#c4c4c4"),
          fontSize: "12px",
          fontWeight: 500,
        },
        offsetX: -8,
      },
    },
    grid: {
      borderColor: "rgba(255,255,255,0.1)",
      xaxis: {
        lines: {
          show: false,
        },
      },
      yaxis: {
        lines: {
          show: false,
        },
      },
      padding: {
        top: 5,
        right: 5,
        bottom: 5,
        left: 5,
      },
    },
    tooltip: {
      theme: "dark",
      x: {
        show: true,
      },
      y: {
        title: {
          formatter: function () {
            return "Mentions:";
          },
        },
        formatter: function (val) {
          return val;
        },
      },
      marker: {
        show: false,
      },
      style: {
        fontSize: '14px',
        fontFamily: 'Inter, system-ui, sans-serif',
      },
    },
  };

  const wordsChartOptions = {
    chart: {
      type: "bar",
      height: 250,
      background: "transparent",
      toolbar: {
        show: false,
      },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        borderRadius: 4,
        columnWidth: '65%',
        distributed: true,
      },
    },
    colors: [
      themeColor === "purple" ? "#c084fc" : themeColor === "emerald" ? "#34d399" : "#fb7185",
      themeColor === "purple" ? "#a855f7" : themeColor === "emerald" ? "#10b981" : "#f43f5e",
      themeColor === "purple" ? "#8b5cf6" : themeColor === "emerald" ? "#059669" : "#e11d48",
      themeColor === "purple" ? "#7c3aed" : themeColor === "emerald" ? "#047857" : "#be123c",
    ],
    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    xaxis: {
      categories: prepareWordsChartData().categories,
      labels: {
        style: {
          colors: Array(8).fill("#c4c4c4"),
          fontSize: "12px",
        },
        rotate: -45,
        rotateAlways: false,
        hideOverlappingLabels: true,
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: "#c4c4c4",
          fontSize: "12px",
        },
      },
    },
    grid: {
      borderColor: "rgba(255,255,255,0.1)",
      xaxis: {
        lines: {
          show: false,
        },
      },
      yaxis: {
        lines: {
          show: true,
          opacity: 0.1,
        },
      },
    },
    tooltip: {
      theme: "dark",
    },
  };

  const getTextClass = () => {
    switch (themeColor) {
      case "emerald":
        return "text-emerald-400";
      case "rose":
        return "text-rose-400";
      default:
        return "text-purple-400";
    }
  };
  
  const getSentimentColor = () => {
    switch (data?.sentiment?.overall_mood) {
      case "positive":
        return "text-green-500";
      case "negative":
        return "text-red-500";
      default:
        return "text-yellow-500";
    }
  };

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center overflow-hidden">
        <div className="relative">
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full opacity-40 blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 180],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
            }}
          />
          <div className="relative z-10 flex flex-col items-center">
            <motion.span
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1, rotate: 360 }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="text-4xl mb-4"
            >
              🌟
            </motion.span>
            <span className={`text-3xl font-bold ${getTextClass()}`}>Loading trend data</span>
          </div>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-8">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1, rotate: [0, 10, -10, 0] }}
          transition={{ duration: 0.6, type: "spring" }}
          className="text-rose-500 mb-6"
        >
          <AlertTriangle size={88} strokeWidth={1.5} />
        </motion.div>
        <h1 className="text-3xl text-rose-400 mb-4 font-bold">Oops! Connection Error</h1>
        <p className="text-gray-300 mb-6 text-center max-w-md text-xl">{error}</p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.98 }}
          className="px-6 py-3 bg-gradient-to-r from-rose-600 to-orange-500 rounded-xl text-white font-medium shadow-lg transition-all hover:shadow-rose-500/30"
          onClick={() => window.location.reload()}
        >
          Try Again
        </motion.button>
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-bl from-gray-900 via-gray-800 to-black text-gray-100 pt-24 pb-20 p-6 relative overflow-hidden">
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.header 
            initial={{ y: -50, opacity: 0 }} 
            animate={{ y: 0, opacity: 1 }} 
            transition={{ duration: 0.6 }} 
            className="mb-8"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-2">
              <motion.h1
                className={`text-3xl font-bold ${getTextClass()} mb-2 sm:mb-0`}
                animate={{
                  textShadow: [
                    `0 0 10px ${themeColor === "purple" ? "#a855f7" : themeColor === "emerald" ? "#10b981" : "#f43f5e"}30`,
                    `0 0 20px ${themeColor === "purple" ? "#a855f7" : themeColor === "emerald" ? "#10b981" : "#f43f5e"}40`,
                    `0 0 10px ${themeColor === "purple" ? "#a855f7" : themeColor === "emerald" ? "#10b981" : "#f43f5e"}30`,
                  ],
                }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                <span className="relative inline-block">
                  <Sparkles className="absolute -top-7 -left-7 h-6 w-6 text-yellow-300 animate-pulse" />
                  Social Media Trends Dashboard
                </span>
              </motion.h1>

              <div className="flex items-center text-sm backdrop-blur-md bg-gray-800/40 px-4 py-2.5 rounded-xl border border-gray-700">
                <Clock size={16} className={`mr-2 ${getTextClass()}`} />
                <span className="font-mono tracking-wide mr-4">Next refresh: {formatCountdown()}</span>
                <span className="text-gray-400">Last updated: {lastUpdated.toLocaleTimeString()}</span>
              </div>
            </div>
            <div className="flex flex-wrap items-center text-sm text-gray-400 mt-1 backdrop-blur-md bg-gray-800/30 px-4 py-3 rounded-lg">
              <span className="mr-6 flex items-center">
                <span className={`font-medium mr-2`}>Domain:</span>
                {data?.domain || 'N/A'}
              </span>
              <span className="mr-6 flex items-center">
                <span className={`font-medium mr-2`}>Date:</span>
                {data?.timestamp ? new Date(data.timestamp).toLocaleDateString() : 'N/A'}
              </span>
              <span className="flex items-center">
                <span className={`font-medium mr-2`}>Sentiment:</span>
                <span className={`font-medium ${getSentimentColor()}`}>
                  {data?.sentiment?.overall_mood ? 
                    data.sentiment.overall_mood.charAt(0).toUpperCase() + data.sentiment.overall_mood.slice(1) : 
                    'Unknown'
                  }
                </span>
              </span>
            </div>
          </motion.header>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.4 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <h3 className={`${getTextClass()} font-medium text-lg mb-4 flex items-center`}>
                <TrendingUp className="mr-2" size={18} />
                Top Trends
              </h3>

              <div className="grid grid-cols-1 gap-2">
                {data?.top_trends?.map((trend, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index, duration: 0.5 }}
                    className={`px-3 py-2 rounded-lg text-sm font-medium flex items-center ${
                      themeColor === "purple"
                        ? "bg-purple-900/40 border-l-4 border-purple-500"
                        : themeColor === "emerald"
                        ? "bg-emerald-900/40 border-l-4 border-emerald-500"
                        : "bg-rose-900/40 border-l-4 border-rose-500"
                    }`}
                  >
                    <span className="text-gray-300 mr-2 w-5 text-center font-mono">{index + 1}</span>
                    {trend}
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Popular Hashtags - Updated to horizontal bar chart */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.5 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors md:col-span-2"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <h3 className={`${getTextClass()} font-medium text-lg mb-3 flex items-center`}>
                <span className="text-xl mr-2">#</span>Popular Hashtags
              </h3>
              <div className="h-72">
                <Chart
                  options={hashtagsChartOptions}
                  series={[{ 
                    name: "Mentions", 
                    data: prepareHashtagsChartData().values,
                  }]}
                  type="bar"
                  height="100%"
                />
              </div>
            </motion.div>

            {/* Top Words - Updated to vertical bar chart */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.6 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors lg:col-span-3"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <h3 className={`${getTextClass()} font-medium text-lg mb-3`}>Top Words</h3>
              <div className="h-64">
                <Chart
                  options={wordsChartOptions}
                  series={[{ name: "Occurrences", data: prepareWordsChartData().values }]}
                  type="bar"
                  height="100%"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <h3 className={`${getTextClass()} font-medium text-lg mb-4 text-center`}>Sentiment Analysis</h3>
              <div className="h-64 flex items-center justify-center">
                <div className="w-full h-full">
                  <Chart options={sentimentGaugeOptions} series={[prepareSentimentGaugeData()]} type="radialBar" height="100%" />
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-4">
                <div
                  className={`p-3 rounded-lg bg-opacity-20 ${
                    themeColor === "purple" ? "bg-purple-900/20" : themeColor === "emerald" ? "bg-emerald-900/20" : "bg-rose-900/20"
                  }`}
                >
                  <div className="text-xs text-gray-400 mb-1">Positive</div>
                  <div className="text-lg font-medium flex items-center">
                    <div className={`w-3 h-3 rounded-full mr-2 ${themeColor === "emerald" ? "bg-emerald-500" : "bg-green-500"}`}></div>
                    {data.sentiment.data.transformer?.positive_percentage?.toFixed(1)}%
                  </div>
                </div>
                <div
                  className={`p-3 rounded-lg bg-opacity-20 ${
                    themeColor === "purple" ? "bg-purple-900/20" : themeColor === "emerald" ? "bg-emerald-900/20" : "bg-rose-900/20"
                  }`}
                >
                  <div className="text-xs text-gray-400 mb-1">Negative</div>
                  <div className="text-lg font-medium flex items-center">
                    <div className="w-3 h-3 rounded-full mr-2 bg-rose-500"></div>
                    {(100 - data.sentiment.data.transformer?.positive_percentage)?.toFixed(1)}%
                  </div>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <h3 className={`${getTextClass()} font-medium text-lg mb-4 text-center`}>Sentiment Metrics</h3>
              <div className="h-64">
                <Chart options={confidenceRadarOptions} series={confidenceRadarOptions.series} type="radar" height="100%" />
              </div>
              <div className="mt-4 flex justify-center space-x-2">
                <div className="flex items-center">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      themeColor === "purple" ? "bg-purple-500" : themeColor === "emerald" ? "bg-emerald-500" : "bg-rose-500"
                    } mr-1`}
                  ></div>
                  <span className="text-xs text-gray-400">Metrics</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: 0.3 }}
              className="backdrop-blur-md bg-gray-700/50 md:col-span-2 lg:col-span-1 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <h3 className={`${getTextClass()} font-medium text-lg mb-3 text-center`}>Expert Analysis</h3>
              <div
                className={`p-4 rounded-lg ${
                  themeColor === "purple"
                    ? "bg-purple-900/20 border-purple-800/20"
                    : themeColor === "emerald"
                    ? "bg-emerald-900/20 border-emerald-800/20"
                    : "bg-rose-900/20 border-rose-800/20"
                } border`}
              >
                <p className="text-gray-300 text-sm">{data.ai_analysis?.sentiment_analysis || "No sentiment analysis available"}</p>
              </div>
              <div className="mt-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gray-800/80 p-3 rounded-lg">
                    <div className="text-xs text-gray-400 mb-1">Polarity</div>
                    <div className="text-lg font-mono font-medium flex items-center">
                      {data.sentiment.data.textblob?.avg_polarity?.toFixed(3) || "N/A"}
                      {data.sentiment.data.textblob?.avg_polarity > 0 && <ArrowUp size={16} className="ml-1 text-green-500" />}
                      {data.sentiment.data.textblob?.avg_polarity < 0 && <ArrowDown size={16} className="ml-1 text-red-500" />}
                    </div>
                  </div>
                  <div className="bg-gray-800/80 p-3 rounded-lg">
                    <div className="text-xs text-gray-400 mb-1">Subjectivity</div>
                    <div className="text-lg font-mono font-medium">{data.sentiment.data.textblob?.avg_subjectivity?.toFixed(3) || "N/A"}</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
          
          {/* AI Insights and Content Recommendations */}
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* AI Insights */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className={`${getTextClass()} font-medium text-xl`}>
                  <div className="flex items-center">
                    <Zap className="mr-2" size={20} />
                    AI Insights
                  </div>
                </h3>
              </div>
              
              <div className="mb-4">
                <h4 className={`${getTextClass()} text-sm font-semibold mb-2 uppercase tracking-wider`}>Key Findings:</h4>
                <ul className="list-disc pl-5 space-y-2">
                  {data.ai_analysis?.key_insights?.map((insight, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 * index, duration: 0.4 }}
                      className="text-gray-200 text-sm"
                    >
                      {insight}
                    </motion.li>
                  ))}
                </ul>
              </div>
              
              <div className="mt-4 pt-3 border-t border-gray-600/30">
                <h4 className={`${getTextClass()} text-sm font-semibold mb-2 uppercase tracking-wider`}>Trend Prediction:</h4>
                <p className="text-gray-300 text-sm">{data.ai_analysis?.trend_prediction || "No prediction available"}</p>
              </div>
            </motion.div>
            
            {/* Content Recommendations - Updated to 2-column card layout */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="backdrop-blur-md bg-gray-700/50 p-5 rounded-xl border border-gray-600/50 hover:border-gray-500/60 transition-colors"
              whileHover={{
                boxShadow:
                  themeColor === "purple"
                    ? "0 8px 25px -5px rgba(168, 85, 247, 0.25)"
                    : themeColor === "emerald"
                    ? "0 8px 25px -5px rgba(16, 185, 129, 0.25)"
                    : "0 8px 25px -5px rgba(244, 63, 94, 0.25)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className={`${getTextClass()} font-medium text-xl`}>
                  <div className="flex items-center">
                    <Database className="mr-2" size={20} />
                    Content Recommendations
                  </div>
                </h3>
              </div>
              
              <div>
                <h4 className={`${getTextClass()} text-sm font-semibold mb-3 uppercase tracking-wider`}>Suggested Content Strategies:</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {data.ai_analysis?.content_recommendations?.map((recommendation, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.05 * index, duration: 0.4 }}
                      className={`p-4 rounded-lg shadow-md border ${
                        themeColor === "purple"
                          ? "bg-purple-900/30 border-purple-800/30"
                          : themeColor === "emerald"
                          ? "bg-emerald-900/30 border-emerald-800/30"
                          : "bg-rose-900/30 border-rose-800/30"
                      } hover:shadow-lg transition-all duration-300 flex flex-col h-full`}
                      whileHover={{ y: -2 }}
                    >
                      <div className="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">Strategy {index + 1}</div>
                      <p className="text-gray-200 text-sm leading-relaxed flex-1">{recommendation}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
              
              <div className="mt-4 pt-3 border-t border-gray-600/30">
                <h4 className={`${getTextClass()} text-sm font-semibold mb-2 uppercase tracking-wider`}>Summary:</h4>
                <p className="text-gray-300 text-sm">{data.ai_analysis?.summary || "No summary available"}</p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default SocialMediaDashboard;
