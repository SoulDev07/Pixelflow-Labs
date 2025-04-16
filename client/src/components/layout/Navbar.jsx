import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Video, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function Navbar() {
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
    <>
      <motion.nav
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
          scrolled ? "py-3 bg-gray-900/90 backdrop-blur-md shadow-lg shadow-black/20" : "py-5 bg-transparent"
        }`}
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center"
            >
              <Link to="/" className="flex items-center group">
                <div className="relative">
                  <div className="absolute -inset-1 bg-purple-600/40 rounded-full opacity-70 group-hover:opacity-100 blur-sm group-hover:blur transition"></div>
                  <div className="relative bg-gray-900 rounded-full p-2 flex items-center justify-center">
                    <Video className="h-6 w-6 text-purple-400 group-hover:text-purple-300 transition-all" />
                  </div>
                </div>
                <div className="ml-3">
                  <span className="font-bold text-2xl tracking-tight text-purple-400">Pixel</span>
                  <span className="font-bold text-2xl">Flow</span>
                </div>
              </Link>
            </motion.div>

            <div className="hidden md:flex items-center space-x-4">
              <Link to="/dashboard">
                <Button variant="ghost" size="sm" className="text-purple-400 hover:text-purple-300 hover:bg-purple-900/50">
                  Dashboard
                </Button>
              </Link>
              <div className="h-4 w-px bg-gray-700"></div>
              <Link to="/" className="text-purple-400 hover:text-purple-300 text-sm transition-colors">
                Home
              </Link>
              <Link to="/text-to-video">
                <Button size="sm" className="bg-purple-600 hover:bg-purple-700 text-white">
                  Create Video
                </Button>
              </Link>
            </div>

            <div className="md:hidden flex items-center">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-md text-purple-400 hover:text-purple-300 focus:outline-none"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        <AnimatedMobileMenu isOpen={mobileMenuOpen} setIsOpen={setMobileMenuOpen} />
      </motion.nav>
    </>
  );
}

function AnimatedMobileMenu({ isOpen, setIsOpen }) {
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: isOpen ? 1 : 0, height: isOpen ? "auto" : 0 }}
      transition={{ duration: 0.3 }}
      className="md:hidden overflow-hidden bg-gray-800 border-t border-gray-700 mt-2"
    >
      <div className="px-4 py-4 space-y-3">
        <MobileNavLink href="/" onClick={() => setIsOpen(false)}>
          Home
        </MobileNavLink>
        <MobileNavLink href="/dashboard" onClick={() => setIsOpen(false)}>
          Dashboard
        </MobileNavLink>
        <div className="pt-2">
          <Link to="/text-to-video" onClick={() => setIsOpen(false)}>
            <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">Create Video</Button>
          </Link>
        </div>
      </div>
    </motion.div>
  );
}

function MobileNavLink({ href, onClick, children }) {
  return (
    <a
      href={href}
      onClick={onClick}
      className="block px-3 py-2 text-gray-300 hover:text-white font-medium hover:bg-gray-700 rounded-md transition-colors duration-200"
    >
      {children}
    </a>
  );
}
