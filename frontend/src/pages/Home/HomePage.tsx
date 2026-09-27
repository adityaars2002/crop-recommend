import { Link } from 'react-router-dom';
import {
  Sprout,
  Microscope,
  ArrowRight,
  BarChart3,
  Shield,
  Zap,
  Leaf,
  CloudRain,
  FlaskConical,
} from 'lucide-react';
import { Card, Button } from '../../components/ui';

export default function HomePage() {
  return (
    <div className="motion-safe:animate-[fadeIn_0.4s_ease-out]">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-emerald-700 via-emerald-800 to-stone-900">
        {/* Background decorative elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 h-72 w-72 rounded-full bg-emerald-400 blur-3xl" />
          <div className="absolute bottom-10 right-10 h-96 w-96 rounded-full bg-teal-400 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 md:py-28">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm text-emerald-100 backdrop-blur-sm mb-6">
              <Leaf className="h-4 w-4" />
              <span>AI-Powered Agriculture Platform</span>
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight tracking-tight">
              Smarter Farming Starts with{' '}
              <span className="text-emerald-300">Data</span>
            </h1>
            <p className="mt-5 text-lg md:text-xl text-emerald-100/80 max-w-2xl leading-relaxed">
              Make data-driven agricultural decisions. Choose the right crop for your soil
              and climate, and detect plant diseases early — all powered by machine learning.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link to="/crop-recommendation">
                <Button size="lg" className="bg-white text-emerald-800 hover:bg-emerald-50 shadow-lg shadow-black/10">
                  Get Crop Advice
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/disease-detection">
                <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10 hover:text-white">
                  Detect Disease
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 -mt-12 relative z-10">
        <div className="grid md:grid-cols-2 gap-6">
          {/* Crop Recommendation Card */}
          <Link to="/crop-recommendation" className="group">
            <Card hover className="h-full !p-0 overflow-hidden">
              <div className="p-6 md:p-8">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 mb-4 group-hover:scale-105 transition-transform">
                  <Sprout className="h-6 w-6" />
                </div>
                <h2 className="text-xl font-bold text-stone-900 mb-2">
                  Crop Recommendation
                </h2>
                <p className="text-stone-500 text-sm leading-relaxed mb-4">
                  Enter your soil nutrient levels and environmental conditions. Our Random Forest
                  model analyzes 7 parameters to recommend the top 3 most suitable crops for your land.
                </p>
                <span className="inline-flex items-center gap-1 text-sm font-semibold text-emerald-700 group-hover:gap-2 transition-all">
                  Start Analysis <ArrowRight className="h-4 w-4" />
                </span>
              </div>
              <div className="h-1.5 bg-gradient-to-r from-emerald-500 to-teal-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Card>
          </Link>

          {/* Disease Detection Card */}
          <Link to="/disease-detection" className="group">
            <Card hover className="h-full !p-0 overflow-hidden">
              <div className="p-6 md:p-8">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-100 text-sky-700 mb-4 group-hover:scale-105 transition-transform">
                  <Microscope className="h-6 w-6" />
                </div>
                <h2 className="text-xl font-bold text-stone-900 mb-2">
                  Plant Disease Detection
                </h2>
                <p className="text-stone-500 text-sm leading-relaxed mb-4">
                  Upload a photo of a plant leaf. Our MobileNetV2 deep learning model classifies
                  it across 38 disease categories covering 14 crop species with high accuracy.
                </p>
                <span className="inline-flex items-center gap-1 text-sm font-semibold text-sky-700 group-hover:gap-2 transition-all">
                  Upload Image <ArrowRight className="h-4 w-4" />
                </span>
              </div>
              <div className="h-1.5 bg-gradient-to-r from-sky-500 to-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Card>
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 md:py-24">
        <div className="text-center mb-14">
          <h2 className="text-2xl md:text-3xl font-bold text-stone-900">How It Works</h2>
          <p className="mt-3 text-stone-500 max-w-lg mx-auto">
            Three simple steps to smarter agriculture decisions
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              step: '01',
              icon: <FlaskConical className="h-6 w-6" />,
              title: 'Input Your Data',
              desc: 'Enter soil nutrients, pH, temperature, humidity and rainfall — or upload a leaf photo.',
            },
            {
              step: '02',
              icon: <Zap className="h-6 w-6" />,
              title: 'AI Analysis',
              desc: 'Our trained ML models process your data using Random Forest and MobileNetV2 architectures.',
            },
            {
              step: '03',
              icon: <BarChart3 className="h-6 w-6" />,
              title: 'Get Results',
              desc: 'Receive ranked crop recommendations or disease diagnosis with confidence scores.',
            },
          ].map((item) => (
            <div key={item.step} className="text-center">
              <div className="relative mx-auto mb-5">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700 mx-auto">
                  {item.icon}
                </div>
                <span className="absolute -top-2 -right-2 flex h-7 w-7 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white">
                  {item.step}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-stone-900 mb-2">{item.title}</h3>
              <p className="text-sm text-stone-500 leading-relaxed max-w-xs mx-auto">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Capabilities */}
      <section className="bg-white border-y border-stone-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 md:py-24">
          <div className="text-center mb-14">
            <h2 className="text-2xl md:text-3xl font-bold text-stone-900">
              Why AgriSense?
            </h2>
            <p className="mt-3 text-stone-500 max-w-lg mx-auto">
              Built on proven ML models with real agricultural data
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: <Sprout className="h-5 w-5" />,
                title: '22 Crop Classes',
                desc: 'Random Forest model trained on comprehensive crop data',
                color: 'bg-emerald-50 text-emerald-700',
              },
              {
                icon: <Microscope className="h-5 w-5" />,
                title: '38 Disease Classes',
                desc: 'Covering 14 crop species with ~97% test accuracy',
                color: 'bg-sky-50 text-sky-700',
              },
              {
                icon: <CloudRain className="h-5 w-5" />,
                title: '7 Parameters',
                desc: 'NPK, temperature, humidity, pH, and rainfall analysis',
                color: 'bg-amber-50 text-amber-700',
              },
              {
                icon: <Shield className="h-5 w-5" />,
                title: 'Validated Models',
                desc: '99.55% crop accuracy · 97.05% disease accuracy',
                color: 'bg-violet-50 text-violet-700',
              },
            ].map((cap) => (
              <Card key={cap.title} className="text-center" hover>
                <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${cap.color} mx-auto mb-3`}>
                  {cap.icon}
                </div>
                <h3 className="text-sm font-semibold text-stone-900 mb-1">{cap.title}</h3>
                <p className="text-xs text-stone-500 leading-relaxed">{cap.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 md:py-24">
        <Card className="!p-0 overflow-hidden bg-gradient-to-br from-emerald-700 to-stone-900 border-none">
          <div className="p-8 md:p-12 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">
              Ready to get started?
            </h2>
            <p className="text-emerald-100/80 max-w-md mx-auto mb-8">
              Analyze your soil conditions or diagnose plant diseases in minutes.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link to="/crop-recommendation">
                <Button size="lg" className="bg-white text-emerald-800 hover:bg-emerald-50">
                  Recommend Crops
                </Button>
              </Link>
              <Link to="/disease-detection">
                <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10 hover:text-white">
                  Detect Disease
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      </section>
    </div>
  );
}
