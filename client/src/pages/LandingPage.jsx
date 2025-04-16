import { useState, useEffect, useRef } from "react";
import { motion, useScroll, useSpring, useAnimation } from "framer-motion";
import { ChevronDown, Video, Wand2, Zap, Code2, Play, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

const useScrollAnimation = () => {
  const controls = useAnimation();
  const ref = useRef(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          controls.start("visible");
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [controls]);

  return { ref, controls, isVisible };
};

export default function PixelFlowLandingPage() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  const heroAnimation = useScrollAnimation();
  const featureAnimation1 = useScrollAnimation();
  const featureAnimation2 = useScrollAnimation();
  const featureAnimation3 = useScrollAnimation();

  const showcaseVideos = [
    {
      title: "Product Showcase",
      thumbnail: "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1074&q=80",
      video: "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
    },
    {
      title: "Brand Story",
      thumbnail: "https://images.unsplash.com/photo-1601933513793-a3ca10d50c93?ixlib=rb-4.0.3&auto=format&fit=crop&w=1170&q=80",
      video: "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_2mb.mp4",
    },
    {
      title: "Social Ad",
      thumbnail: "https://images.unsplash.com/photo-1561070791-2526d30994b5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1964&q=80",
      video: "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_5mb.mp4",
    },
  ];

  const [activeVideo, setActiveVideo] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 transition-colors duration-300">
      <motion.div className="fixed top-0 left-0 right-0 h-1 bg-purple-600 z-50" style={{ scaleX }} />
      <Navbar />
      <main>
        <section className="h-screen flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 z-0 opacity-30">
            <video
              autoPlay
              muted
              loop
              className="w-full h-full object-cover"
              poster="https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
            >
              <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-a-city-11748-large.mp4" type="video/mp4" />
            </video>
            <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/60 to-gray-900/10"></div>
          </div>

          <motion.div
            ref={heroAnimation.ref}
            initial="hidden"
            animate={heroAnimation.controls}
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 },
            }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-center z-10 max-w-4xl px-4"
          >
            <h2 className="text-5xl md:text-7xl font-extrabold mb-6">
              <span className="text-purple-400">Transform Text to Video</span> with AI
            </h2>
            <p className="text-xl md:text-2xl mb-8">
              Generate stunning social media content in minutes with our AI-driven text-to-video platform
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/text-to-video">
                <Button
                  size="lg"
                  className="text-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-8 py-6 w-full sm:w-auto"
                >
                  Create Your First Video
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button
                  size="lg"
                  variant="outline"
                  className="text-lg px-8 py-6 w-full sm:w-auto border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-white"
                >
                  View Analytics
                </Button>
              </Link>
            </div>
          </motion.div>
          <motion.div
            className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ChevronDown className="w-8 h-8 text-purple-400" />
          </motion.div>
        </section>

        <section className="py-20 bg-gray-800">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h3 className="text-3xl font-bold mb-6 text-purple-200">See What PixelFlow Can Create</h3>
              <p className="text-xl max-w-2xl mx-auto text-gray-300">
                From product showcases to brand stories, create professional videos with just text input
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {showcaseVideos.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="relative group overflow-hidden rounded-xl"
                >
                  <div className="aspect-video bg-gray-700 overflow-hidden rounded-xl">
                    <img
                      src={item.thumbnail}
                      alt={item.title}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-70"></div>
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full"
                        onClick={() => setActiveVideo(item.video)}
                      >
                        <Play className="h-8 w-8" />
                      </button>
                    </div>
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-4">
                    <h4 className="text-xl font-semibold">{item.title}</h4>
                    <p className="text-gray-300">AI-generated video</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 bg-gray-900">
          <div className="container mx-auto px-4">
            <motion.div
              ref={featureAnimation1.ref}
              initial="hidden"
              animate={featureAnimation1.controls}
              variants={{
                visible: { opacity: 1, y: 0 },
                hidden: { opacity: 0, y: 50 },
              }}
              transition={{ duration: 0.5 }}
              className="mb-20 text-center"
            >
              <h3 className="text-3xl font-bold mb-6 text-purple-200">Why Choose PixelFlow</h3>
              <p className="text-xl max-w-2xl mx-auto text-gray-300">
                Create professional-looking videos for your social media campaigns without any video editing skills
              </p>
            </motion.div>
            <div className="grid md:grid-cols-3 gap-10">
              {[
                {
                  icon: <Wand2 className="h-12 w-12" />,
                  title: "AI-Powered Creation",
                  description:
                    "Our state-of-the-art AI understands context, style, and brand voice to generate captivating videos that resonate with your audience",
                  gradient: "from-cyan-500/20 to-blue-500/20",
                  borderColor: "border-cyan-500/30",
                  iconBg: "bg-cyan-500/10",
                  iconColor: "text-cyan-400",
                },
                {
                  icon: <Zap className="h-12 w-12" />,
                  title: "Lightning Fast Results",
                  description:
                    "Generate complete video campaigns in minutes instead of days, accelerating your content pipeline and time-to-market by up to 10x",
                  gradient: "from-amber-500/20 to-yellow-500/20",
                  borderColor: "border-yellow-500/30",
                  iconBg: "bg-yellow-500/10",
                  iconColor: "text-yellow-400",
                },
                {
                  icon: <Code2 className="h-12 w-12" />,
                  title: "Zero Learning Curve",
                  description:
                    "Simply describe your vision in plain text, and watch as our AI transforms your words into professional-grade video content instantly",
                  gradient: "from-green-500/20 to-emerald-500/20",
                  borderColor: "border-green-500/30",
                  iconBg: "bg-green-500/10",
                  iconColor: "text-green-400",
                },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  ref={index === 0 ? featureAnimation1.ref : index === 1 ? featureAnimation2.ref : featureAnimation3.ref}
                  initial="hidden"
                  animate={index === 0 ? featureAnimation1.controls : index === 1 ? featureAnimation2.controls : featureAnimation3.controls}
                  variants={{
                    visible: { opacity: 1, y: 0 },
                    hidden: { opacity: 0, y: 50 },
                  }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                  className={`bg-gradient-to-br ${feature.gradient} p-8 rounded-xl shadow-lg text-center hover:shadow-xl transition-shadow duration-300 border ${feature.borderColor} backdrop-blur-sm`}
                >
                  <div className={`${feature.iconBg} w-20 h-20 mx-auto rounded-full flex items-center justify-center mb-6`}>
                    <div className={feature.iconColor}>{feature.icon}</div>
                  </div>
                  <h4 className="text-2xl font-semibold mb-4 bg-gradient-to-r from-white to-gray-300 text-transparent bg-clip-text">
                    {feature.title}
                  </h4>
                  <p className="text-gray-300 leading-relaxed">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 relative overflow-hidden bg-gradient-to-b from-gray-800 to-gray-900">
          <div className="absolute inset-0 opacity-20">
            <div className="absolute inset-0 bg-grid-white/10 bg-grid-16 mix-blend-soft-light"></div>
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
            <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
          </div>
          <div className="container mx-auto px-4 relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
              viewport={{ once: true }}
              className="max-w-4xl mx-auto text-center"
            >
              <span className="inline-block bg-purple-900 border border-purple-500/30 text-purple-200 text-sm font-medium py-1 px-3 rounded-full mb-4">
                PROJECT SHOWCASE
              </span>
              <h3 className="text-4xl md:text-5xl font-bold mb-6 text-gray-100">
                Ready to Revolutionize Your <br />
                <span className="text-purple-400">Content Creation?</span>
              </h3>
              <p className="text-xl md:text-2xl mb-10 text-gray-300 max-w-3xl mx-auto">
                Experience how AI can transform your creative workflow and help you create professional videos without any editing skills.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-5 mb-8">
                <Link to="/text-to-video">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      size="lg"
                      className="text-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white px-8 py-6 font-bold shadow-lg transition-all"
                    >
                      Create Your First Video Now <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </motion.div>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
      {activeVideo && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
          onClick={() => setActiveVideo(null)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="relative w-full max-w-4xl aspect-video bg-black rounded-xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="absolute top-4 right-4 bg-black/40 hover:bg-black/60 rounded-full p-2 text-white z-10"
              onClick={() => setActiveVideo(null)}
            >
              ✕
            </button>
            <video src={activeVideo} controls autoPlay className="w-full h-full" />
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
