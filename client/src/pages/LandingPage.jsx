import { useState, useEffect, useRef } from 'react'
import { motion, useScroll, useTransform, useSpring, useAnimation } from 'framer-motion'
import { Moon, Sun, ChevronDown } from 'lucide-react'
import { Button } from "@/components/ui/button"
import useTheme from '@/hooks/useTheme'

const useScrollAnimation = () => {
  const controls = useAnimation()
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          controls.start('visible')
        }
      },
      { threshold: 0.1 }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [controls])

  return { ref, controls, isVisible }
}

export default function CoolLandingPage() {
  const { theme, toggleTheme } = useTheme()
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  })

  const heroAnimation = useScrollAnimation()
  const featureAnimation1 = useScrollAnimation()
  const featureAnimation2 = useScrollAnimation()
  const featureAnimation3 = useScrollAnimation()

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-primary z-50"
        style={{ scaleX }}
      />
      <nav className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-2xl font-bold">CoolBrand</h1>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Button variant="ghost" size="icon" onClick={toggleTheme}>
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </Button>
          </motion.div>
        </div>
      </nav>

      <main>
        <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
          <motion.div
            ref={heroAnimation.ref}
            initial="hidden"
            animate={heroAnimation.controls}
            variants={{
              visible: { opacity: 1, y: 0 },
              hidden: { opacity: 0, y: 50 }
            }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-center z-10"
          >
            <h2 className="text-5xl md:text-7xl font-extrabold mb-6">Welcome to the Future</h2>
            <p className="text-xl md:text-2xl mb-8">Experience innovation like never before</p>
            <Button size="lg" className="text-lg bg-secondary text-primary hover:text-black px-8 py-6">
              Get Started
            </Button>
          </motion.div>
          <motion.div
            className="absolute inset-0 z-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          >
            {[...Array(50)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute rounded-full bg-primary/10"
                style={{
                  width: Math.random() * 100 + 50,
                  height: Math.random() * 100 + 50,
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  duration: Math.random() * 2 + 1,
                  repeat: Infinity,
                  repeatType: 'reverse',
                }}
              />
            ))}
          </motion.div>
          <motion.div
            className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <ChevronDown className="w-8 h-8" />
          </motion.div>
        </section>

        <section className="py-20 bg-muted">
          <div className="container mx-auto px-4">
            <motion.div
              ref={featureAnimation1.ref}
              initial="hidden"
              animate={featureAnimation1.controls}
              variants={{
                visible: { opacity: 1, y: 0 },
                hidden: { opacity: 0, y: 50 }
              }}
              transition={{ duration: 0.5 }}
              className="mb-20"
            >
              <h3 className="text-3xl font-bold mb-6">Innovative Features</h3>
              <p className="text-xl">Discover the cutting-edge technology that sets us apart.</p>
            </motion.div>
            <div className="grid md:grid-cols-3 gap-10">
              {[
                { title: "AI-Powered", description: "Harness the power of artificial intelligence" },
                { title: "Eco-Friendly", description: "Sustainable solutions for a better tomorrow" },
                { title: "Seamless Integration", description: "Effortlessly connect with your existing systems" }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  ref={index === 0 ? featureAnimation1.ref : index === 1 ? featureAnimation2.ref : featureAnimation3.ref}
                  initial="hidden"
                  animate={index === 0 ? featureAnimation1.controls : index === 1 ? featureAnimation2.controls : featureAnimation3.controls}
                  variants={{
                    visible: { opacity: 1, y: 0 },
                    hidden: { opacity: 0, y: 50 }
                  }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                  className="bg-card p-6 rounded-lg shadow-lg"
                >
                  <h4 className="text-xl font-semibold mb-4">{feature.title}</h4>
                  <p>{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20">
          <div className="container mx-auto px-4 text-center">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
            >
              <h3 className="text-3xl font-bold mb-6">Ready to Transform Your Experience?</h3>
              <p className="text-xl mb-8">Join us on this exciting journey into the future.</p>
              <Button size="lg" className="text-lg px-8 py-6">
                Get Started Now
              </Button>
            </motion.div>
          </div>
        </section>
      </main>

      <footer className="bg-muted py-10">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 CoolBrand. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}