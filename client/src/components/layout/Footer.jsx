import { Video, Instagram, Twitter, Youtube } from "lucide-react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="bg-gray-800 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-px bg-purple-500/30"></div>

      <div className="container mx-auto px-4 py-4 relative z-10">
        <div className="flex flex-wrap items-center justify-between">
          <Link to="/" className="flex items-center group mb-2 sm:mb-0">
            <div className="relative">
              <div className="absolute -inset-1 bg-purple-600/40 rounded-full opacity-70 group-hover:opacity-100 blur-sm transition"></div>
              <div className="relative bg-gray-800 rounded-full p-1.5">
                <Video className="h-5 w-5 text-purple-400 group-hover:text-purple-300" />
              </div>
            </div>
            <div className="ml-2">
              <span className="font-bold text-xl text-purple-400">Pixel</span>
              <span className="font-bold text-xl text-white">Flow</span>
            </div>
          </Link>
          
          <p className="text-gray-400 text-sm hidden md:block">Transform your ideas into captivating videos</p>

          <div className="flex items-center space-x-3">
            <div className="flex space-x-2 mr-4">
              <SocialIcon icon={<Instagram size={16} />} />
              <SocialIcon icon={<Twitter size={16} />} />
              <SocialIcon icon={<Youtube size={16} />} />
            </div>
            <p className="text-gray-400 text-xs">&copy; {new Date().getFullYear()} PixelFlow Labs</p>
          </div>
        </div>
      </div>
    </footer>
  );
}

function SocialIcon({ icon }) {
  return (
    <a
      href="#"
      className="w-7 h-7 rounded-full bg-gray-700 hover:bg-purple-600 flex items-center justify-center text-gray-400 hover:text-white transition-colors duration-200"
    >
      <div className="relative z-10">{icon}</div>
    </a>
  );
}
