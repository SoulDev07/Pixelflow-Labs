import { useState, useEffect, useRef, createElement } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Wand2,
  Layers,
  DownloadCloud,
  RefreshCw,
  Check,
  Video,
  Zap,
  Palette,
  Film,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

// Sample templates to inspire users
const sampleTemplates = [
  {
    title: "Product Showcase",
    description: "A sleek video highlighting product features with dynamic transitions",
    preset: {
      productName: "EcoFresh Water Bottle",
      description:
        "A sustainable, insulated water bottle that keeps drinks cold for 24 hours or hot for 12 hours. Made from recycled materials with a sleek modern design.",
      scenes:
        "Scene 1: Close-up of bottle with water droplets, rotating slowly\nScene 2: Person hiking, taking a drink\nScene 3: Infographic showing insulation benefits\nScene 4: Product lineup in different colors\nScene 5: Logo and tagline 'Stay Fresh, Go Eco'",
    },
  },
  {
    title: "Testimonial Style",
    description: "Customer-focused video highlighting benefits and satisfaction",
    preset: {
      productName: "DreamSleep Mattress",
      description:
        "A premium memory foam mattress that adapts to your body shape for the perfect night's sleep. Features cooling technology and hypoallergenic materials.",
      scenes:
        "Scene 1: Person waking up refreshed and stretching\nScene 2: Animation of mattress layers and technology\nScene 3: Split screen of peaceful sleep vs tossing and turning\nScene 4: Customer testimonial quotes appearing\nScene 5: Call to action with discount code",
    },
  },
  {
    title: "Tutorial/How-To",
    description: "Step-by-step guide showing your product in action",
    preset: {
      productName: "BlendMaster Pro Blender",
      description:
        "A powerful 1000W blender with 8 speed settings and preset programs for smoothies, soups, and crushing ice. Includes a digital display and touch controls.",
      scenes:
        "Scene 1: Blender on kitchen counter with ingredients around it\nScene 2: Close-up of control panel as settings are selected\nScene 3: Ingredients being added to blender\nScene 4: Blending in action with smooth result\nScene 5: Final smoothie being poured and enjoyed",
    },
  },
];

// Visual elements for the AI processing animation
const aiProcessingSteps = [
  "Analyzing product details...",
  "Generating scene concepts...",
  "Creating visual elements...",
  "Rendering transitions...",
  "Finalizing video output...",
];

// Icons for the loading animation
const loadingIcons = [
  { icon: Wand2, color: "text-teal-400" },
  { icon: Zap, color: "text-blue-400" },
  { icon: Palette, color: "text-purple-400" },
  { icon: Film, color: "text-pink-400" },
  { icon: Star, color: "text-amber-400" },
];

export default function TextToVideo() {
  const [formData, setFormData] = useState({
    productName: "",
    description: "",
    scenes: "",
  });
  const [loading, setLoading] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [currentIconIndex, setCurrentIconIndex] = useState(0);
  const [downloadStatus, setDownloadStatus] = useState(null); // "downloading", "complete", null
  const videoRef = useRef(null);

  // AI processing animation effect - update both step text and icon
  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setCurrentStep((prev) => (prev + 1) % aiProcessingSteps.length);
        setCurrentIconIndex((prev) => (prev + 1) % loadingIcons.length);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.productName || !formData.description || !formData.scenes) {
      toast.error("Please fill out all fields");
      return;
    }

    setLoading(true);
    setVideoUrl(null);
    setCurrentStep(0);

    try {
      // Make the API call to generate video
      const response = await fetch("http://localhost:5000/api/generate-video", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to generate video");
      }

      // Get the response data directly - API returns video URL immediately
      const data = await response.json();
      
      // Set the video URL from the response
      setVideoUrl(data.videoUrl);
      setLoading(false);
      toast.success("Video generated successfully!");
      
    } catch (error) {
      console.error("Error generating video:", error);
      toast.error("Failed to generate video. Please try again.");
      setLoading(false);
      
      // FOR DEMO ONLY: Fall back to sample videos if the real API fails
      // Remove this in production
      if (process.env.NODE_ENV === "development") {
        console.log("DEV MODE: Falling back to sample video");
        setTimeout(() => {
          const sampleVideos = [
            "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
            "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_2mb.mp4",
            "https://assets.mixkit.co/videos/preview/mixkit-animation-of-futuristic-devices-99786-large.mp4",
          ];
          const randomVideo = sampleVideos[Math.floor(Math.random() * sampleVideos.length)];
          setVideoUrl(randomVideo);
          setLoading(false);
          toast.success("Demo video loaded (API fallback)");
        }, 3000);
      }
    }
  };

  const downloadVideo = async () => {
    if (!videoUrl) return;

    try {
      setDownloadStatus("downloading");
      const response = await fetch(videoUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${formData.productName.replace(/\s+/g, "-").toLowerCase()}-video.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setDownloadStatus("complete");

      // Reset status after showing completion
      setTimeout(() => {
        setDownloadStatus(null);
      }, 3000);
    } catch (error) {
      console.error("Error downloading video:", error);
      toast.error("Failed to download video");
      setDownloadStatus(null);
    }
  };

  const applyTemplate = (preset) => {
    setFormData(preset);
    toast.success("Template applied! Customize it or generate right away.");
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Dynamic gradient background */}
      <div className="fixed inset-0 bg-gray-900">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-gradient-to-br from-blue-500 to-cyan-500 blur-[120px] animate-pulse"></div>
          <div className="absolute bottom-0 -right-1/4 w-1/2 h-1/2 bg-gradient-to-br from-fuchsia-500 to-pink-500 blur-[120px] animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 -translate 1/2 w-1/2 h-1/2 bg-gradient-to-br from-emerald-500 to-teal-500 blur-[120px] animate-pulse delay-700"></div>
        </div>
      </div>

      <Navbar />

      <main className="relative z-10 pt-24 pb-20">
        <div className="container mx-auto px-4">
          <div className="max-w-7xl mx-auto">
            {/* Three-column layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left sidebar - Templates */}
              <div className="lg:col-span-3 space-y-6">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
                  <h3 className="text-xl font-semibold mb-4 text-white flex items-center">
                    <Layers className="w-5 h-5 mr-2 text-teal-400" />
                    Quick Templates
                  </h3>
                  <div className="space-y-3">
                    {sampleTemplates.map((template, index) => (
                      <motion.button
                        key={index}
                        onClick={() => applyTemplate(template.preset)}
                        className="w-full p-4 rounded-xl bg-gradient-to-r from-gray-800/50 to-gray-900/50 hover:from-teal-500/20 hover:to-cyan-500/20 border border-white/5 hover:border-teal-500/50 transition-all group"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <h4 className="font-medium text-white mb-2">{template.title}</h4>
                        <p className="text-sm text-gray-400">{template.description}</p>
                      </motion.button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Main content - Form */}
              <div className="lg:col-span-6">
                <motion.div
                  className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/10"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-3xl font-bold mb-8 bg-gradient-to-r from-teal-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
                    Create Your Video
                  </h2>

                  {videoUrl ? (
                    <div className="space-y-6">
                      <div className="relative overflow-hidden rounded-xl bg-black/20 border border-white/10">
                        <video
                          ref={videoRef}
                          className="w-full aspect-video object-contain"
                          src={videoUrl}
                          controls
                          controlsList="nodownload"
                        />

                        <div className="mt-4 flex justify-between items-center p-4">
                          <h3 className="text-white font-medium">
                            {formData.productName} - Video Ad
                          </h3>
                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              className="bg-white/5 border-white/10 hover:bg-white/10 text-white"
                              onClick={() => {
                                setVideoUrl(null);
                              }}
                            >
                              <RefreshCw className="w-4 h-4 mr-2" />
                              New Video
                            </Button>
                            <Button
                              onClick={downloadVideo}
                              className="bg-gradient-to-r from-teal-500 to-blue-500 hover:from-teal-600 hover:to-blue-600 text-white"
                              disabled={downloadStatus === "downloading"}
                            >
                              {downloadStatus === "downloading" && (
                                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                              )}
                              {downloadStatus === "complete" && (
                                <Check className="w-4 h-4 mr-2" />
                              )}
                              {downloadStatus === null && (
                                <DownloadCloud className="w-4 h-4 mr-2" />
                              )}
                              {downloadStatus === "downloading"
                                ? "Downloading..."
                                : downloadStatus === "complete"
                                ? "Downloaded"
                                : "Save Video"}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : loading ? (
                    <div className="flex flex-col items-center justify-center space-y-8 py-12">
                      {/* Loading animation */}
                      <div className="relative w-40 h-40">
                        {/* Rotating circles */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-full h-full rounded-full border-t-4 border-b-4 border-teal-500 animate-spin"></div>
                        </div>
                        <div className="absolute inset-2 flex items-center justify-center">
                          <div className="w-full h-full rounded-full border-t-4 border-b-4 border-blue-500 animate-spin" style={{ animationDuration: "2s" }}></div>
                        </div>
                        <div className="absolute inset-4 flex items-center justify-center">
                          <div className="w-full h-full rounded-full border-t-4 border-b-4 border-purple-500 animate-spin" style={{ animationDuration: "3s" }}></div>
                        </div>

                        {/* Center pulsing icon with animation */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <AnimatePresence mode="wait">
                            <motion.div
                              key={currentIconIndex}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              exit={{ opacity: 0, scale: 0.8 }}
                              transition={{ duration: 0.3 }}
                              className="p-2 rounded-full bg-white bg-opacity-10 backdrop-blur-sm"
                            >
                              {createElement(loadingIcons[currentIconIndex].icon, {
                                className: `w-8 h-8 ${loadingIcons[currentIconIndex].color}`,
                              })}
                            </motion.div>
                          </AnimatePresence>
                        </div>
                      </div>

                      {/* Loading text */}
                      <div className="text-center">
                        <AnimatePresence mode="wait">
                          <motion.p
                            key={currentStep}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="text-xl text-white font-medium"
                          >
                            {aiProcessingSteps[currentStep]}
                          </motion.p>
                        </AnimatePresence>
                        <p className="text-sm text-gray-400 mt-2">This may take a few moments</p>
                      </div>

                      {/* Progress bar */}
                      <div className="w-full max-w-md bg-white/10 rounded-full h-2.5 overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-teal-400 via-blue-500 to-purple-500"
                          initial={{ width: "0%" }}
                          animate={{ width: "100%" }}
                          transition={{
                            duration: 8,
                            ease: "linear",
                            background: {
                              repeat: Infinity,
                              duration: 2,
                            },
                          }}
                        />
                      </div>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-8">
                      <div className="space-y-6">
                        <div className="relative group">
                          <Label htmlFor="productName" className="text-white text-base mb-2 block">
                            Product Name
                          </Label>
                          <Input
                            id="productName"
                            name="productName"
                            value={formData.productName}
                            onChange={handleInputChange}
                            className="bg-white/5 border-white/10 text-white focus:border-teal-500 h-12 rounded-xl transition-all group-hover:border-white/20"
                            placeholder="Enter your product name"
                          />
                          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity -z-10 blur-xl"></div>
                        </div>

                        <div className="relative group">
                          <Label htmlFor="description" className="text-white text-base mb-2 block">
                            Product Description
                          </Label>
                          <Textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleInputChange}
                            className="bg-white/5 border-white/10 text-white focus:border-teal-500 min-h-[120px] rounded-xl transition-all group-hover:border-white/20"
                            placeholder="Describe your product in detail"
                          />
                          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity -z-10 blur-xl"></div>
                        </div>

                        <div className="relative group">
                          <Label htmlFor="scenes" className="text-white text-base mb-2 block">
                            Ad Layout and Scenes
                          </Label>
                          <Textarea
                            id="scenes"
                            name="scenes"
                            value={formData.scenes}
                            onChange={handleInputChange}
                            className="bg-white/5 border-white/10 text-white focus:border-teal-500 min-h-[180px] rounded-xl transition-all group-hover:border-white/20"
                            placeholder="Describe the scenes and layout you want in your video ad (e.g., Scene 1: Product intro with logo, Scene 2: Features demonstration...)"
                          />
                          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity -z-10 blur-xl"></div>
                        </div>

                        <motion.button
                          type="submit"
                          className="w-full h-14 rounded-xl bg-gradient-to-r from-teal-500 via-cyan-500 to-blue-500 text-white font-medium text-lg relative overflow-hidden group"
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.3)_50%,transparent_75%)] bg-[length:250%_250%,100%_100%] animate-shimmer"></div>
                          <span className="relative flex items-center justify-center">
                            <Sparkles className="mr-2 h-5 w-5" />
                            Generate Video
                          </span>
                        </motion.button>
                      </div>
                    </form>
                  )}
                </motion.div>
              </div>

              {/* Right sidebar - Preview & Tips */}
              <div className="lg:col-span-3 space-y-6">
                <motion.div
                  className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/10 sticky top-24"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <h3 className="text-xl font-semibold mb-4 text-white flex items-center">
                    <Wand2 className="w-5 h-5 mr-2 text-blue-400" />
                    Pro Tips
                  </h3>
                  <div className="space-y-4">
                    <p className="text-sm text-gray-400">💡 Be specific about features and benefits.</p>
                    <p className="text-sm text-gray-400">💡 Use descriptive, engaging language.</p>
                    <p className="text-sm text-gray-400">💡 Mention your target audience.</p>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
