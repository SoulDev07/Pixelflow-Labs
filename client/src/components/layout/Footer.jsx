import { Video, Instagram, Twitter, Youtube, Linkedin, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="bg-gray-800 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-px bg-purple-500/30"></div>

      <div className="container mx-auto px-4 pt-16 pb-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
          <div className="space-y-4">
            <Link to="/" className="flex items-center mb-4 group">
              <div className="relative">
                <div className="absolute -inset-1 bg-purple-600/40 rounded-full opacity-70 group-hover:opacity-100 blur-sm transition"></div>
                <div className="relative bg-gray-800 rounded-full p-2">
                  <Video className="h-6 w-6 text-purple-400 group-hover:text-purple-300" />
                </div>
              </div>
              <div className="ml-3">
                <span className="font-bold text-2xl text-purple-400">Pixel</span>
                <span className="font-bold text-2xl text-white">Flow</span>
              </div>
            </Link>

            <p className="text-gray-400">Transform your ideas into captivating videos with our AI-powered text-to-video platform.</p>

            <div className="flex space-x-4 pt-2">
              <SocialIcon icon={<Instagram size={18} />} />
              <SocialIcon icon={<Twitter size={18} />} />
              <SocialIcon icon={<Youtube size={18} />} />
              <SocialIcon icon={<Linkedin size={18} />} />
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-white relative w-fit">
              Quick Links
              <div className="w-1/2 h-[3px] bg-purple-500 mt-1"></div>
            </h3>
            <ul className="space-y-3 text-gray-400">
              <FooterLink href="/">Home</FooterLink>
              <FooterLink href="/text-to-video">Create Video</FooterLink>
              <FooterLink href="/dashboard">Analytics</FooterLink>
              <FooterLink href="/pricing">Pricing</FooterLink>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-white relative w-fit">
              Resources
              <div className="w-1/2 h-[3px] bg-purple-500 mt-1"></div>
            </h3>
            <ul className="space-y-3 text-gray-400">
              <FooterLink href="/blog">Blog</FooterLink>
              <FooterLink href="/help">Help Center</FooterLink>
              <FooterLink href="/tutorials">Tutorials</FooterLink>
              <FooterLink href="/api">API Docs</FooterLink>
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4 text-white relative w-fit">
              Stay Updated
              <div className="w-1/2 h-[3px] bg-purple-500 mt-1"></div>
            </h3>
            <p className="text-gray-400 mb-4">Subscribe to our newsletter for the latest updates.</p>
            <div className="flex">
              <input
                type="email"
                placeholder="Your email address"
                className="bg-gray-700 px-4 py-2 text-sm rounded-l-md focus:outline-none focus:ring-2 focus:ring-purple-600 w-full"
              />
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-r-md text-sm flex items-center">
                <span>Join</span>
                <ArrowRight size={16} className="ml-1" />
              </button>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-700 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm mb-4 md:mb-0">&copy; 2025 PixelFlow. All rights reserved.</p>

          <div className="flex flex-wrap justify-center space-x-6 text-sm text-gray-400">
            <a href="/terms" className="hover:text-purple-400 transition duration-200">
              Terms
            </a>
            <a href="/privacy" className="hover:text-purple-400 transition duration-200">
              Privacy
            </a>
            <a href="/cookies" className="hover:text-purple-400 transition duration-200">
              Cookies
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterLink({ href, children }) {
  return (
    <li>
      <a href={href} className="hover:text-purple-400 transition duration-200 inline-flex items-center group">
        <span className="transform translate-x-0 group-hover:translate-x-1 transition-transform duration-200">{children}</span>
      </a>
    </li>
  );
}

function SocialIcon({ icon }) {
  return (
    <a
      href="#"
      className="w-8 h-8 rounded-full bg-gray-700 hover:bg-purple-600 flex items-center justify-center text-gray-400 hover:text-white transition-colors duration-200"
    >
      <div className="relative z-10">{icon}</div>
    </a>
  );
}
