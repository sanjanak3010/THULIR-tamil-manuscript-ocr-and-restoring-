import React, { useState } from 'react';
import {
  Upload,
  Sparkles,
  FileText,
  Image as ImageIcon,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  BookOpen,
  Copy,
  Download,
  RotateCcw,
  Languages,
  Check,
  Info,
  ShieldAlert,
  Menu,
  X,
  ChevronRight,
  Compass,
  History,
  Award,
  ArrowRight
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  // Navigation & UI Language state
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'explore' | 'about'
  const [uiLanguage, setUiLanguage] = useState('en'); // 'en' | 'ta'
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Upload Form State
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState('palm-leaf');
  const [scriptInput, setScriptInput] = useState('Tamil');

  // Pipeline Data States
  const [manuscriptId, setManuscriptId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const [scriptData, setScriptData] = useState(null);
  const [isIdentifying, setIsIdentifying] = useState(false);

  const [ocrData, setOcrData] = useState(null);
  const [isRunningOCR, setIsRunningOCR] = useState(false);

  const [restorationData, setRestorationData] = useState(null);
  const [isRestoring, setIsRestoring] = useState(false);
  const [restorationError, setRestorationError] = useState('');

  const [modernTamilData, setModernTamilData] = useState(null);
  const [isConvertingModern, setIsConvertingModern] = useState(false);
  const [modernError, setModernError] = useState('');

  const [translationData, setTranslationData] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationError, setTranslationError] = useState('');

  // UI Feedback Copy States
  const [copiedCard, setCopiedCard] = useState(null);

  // Active Pipeline Step Calculation (0..7)
  const currentStep = (() => {
    if (translationData?.english_translation || translationError) return 7;
    if (modernTamilData?.modern_tamil_text || modernError) return 6;
    if (restorationData?.restored_text || restorationError) return 5;
    if (ocrData?.extracted_text || ocrData?.status === 'failed') return 4;
    if (scriptData) return 3;
    if (manuscriptId) return 2;
    if (selectedFile) return 1;
    return 0;
  })();

  // Reset entire form and states
  const handleReset = () => {
    setSelectedFile(null);
    setImagePreview(null);
    setTitle('');
    setSourceType('palm-leaf');
    setScriptInput('Tamil');
    setManuscriptId(null);
    setIsUploading(false);
    setUploadError('');
    setScriptData(null);
    setIsIdentifying(false);
    setOcrData(null);
    setIsRunningOCR(false);
    setRestorationData(null);
    setIsRestoring(false);
    setRestorationError('');
    setModernTamilData(null);
    setIsConvertingModern(false);
    setModernError('');
    setTranslationData(null);
    setIsTranslating(false);
    setTranslationError('');
  };

  // Copy helper with feedback
  const handleCopy = (text, cardName) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedCard(cardName);
    setTimeout(() => setCopiedCard(null), 2000);
  };

  // Export Full Restoration Report as Text file
  const handleDownloadReport = () => {
    if (!ocrData && !restorationData) return;

    const reportContent = `====================================================================
MARUTHULIR (மருதுளிர்) - TAMIL HERITAGE RESTORATION REPORT
====================================================================
Manuscript Title: ${title || 'Untitled Manuscript'}
Source Type:      ${sourceType}
Detected Script:  ${scriptData?.script || scriptInput} (Confidence: ${scriptData?.confidence ? (scriptData.confidence * 100).toFixed(0) + '%' : 'N/A'})
Report Date:      ${new Date().toLocaleString()}
====================================================================

1. RAW OCR TEXT (Sarvam Document AI)
--------------------------------------------------------------------
Status:     ${ocrData?.status || 'N/A'}
Confidence: ${ocrData?.confidence !== null && ocrData?.confidence !== undefined ? (ocrData.confidence * 100).toFixed(0) + '%' : 'Not provided'}
Text:
${ocrData?.extracted_text || 'OCR unavailable - manuscript was not processed'}

2. RESTORED CLASSICAL TAMIL TEXT (Normalized Sandhi & Pulli Dots)
--------------------------------------------------------------------
Status:     ${restorationData?.status || 'N/A'}
Confidence: ${restorationData?.confidence ? (restorationData.confidence * 100).toFixed(0) + '%' : 'N/A'}
Text:
${restorationData?.restored_text || 'N/A'}

Identified Corrections (${restorationData?.corrections?.length || 0}):
${(restorationData?.corrections || []).map(c => ` - ${c.original} -> ${c.corrected} (${c.type}): ${c.explanation}`).join('\n')}

3. MODERN TAMIL PROSE (தற்கால எளிய உரை)
--------------------------------------------------------------------
Status:     ${modernTamilData?.status || 'N/A'}
Text:
${modernTamilData?.modern_tamil_text || 'N/A'}

4. ENGLISH TRANSLATION
--------------------------------------------------------------------
Status:     ${translationData?.status || 'N/A'}
Text:
${translationData?.english_translation || 'N/A'}

[AI Disclaimer: AI-generated translation for historical interpretation. Verify critical epigraphical findings with domain specialists.]
====================================================================
`;

    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(title || 'maruthulir_manuscript').replace(/[^a-z0-9]/gi, '_').toLowerCase()}_report.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Handle File Selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setUploadError('');
      setManuscriptId(null);
      setScriptData(null);
      setOcrData(null);
      setRestorationData(null);
      setRestorationError('');
      setModernTamilData(null);
      setModernError('');
      setTranslationData(null);
      setTranslationError('');
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  // Full Pipeline Executor (Upload -> Identify -> OCR -> Restore -> Modern -> English)
  const handleRunFullPipeline = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select a manuscript image file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setScriptData(null);
    setOcrData(null);
    setRestorationData(null);
    setRestorationError('');
    setModernTamilData(null);
    setModernError('');
    setTranslationData(null);
    setTranslationError('');

    let currentId = manuscriptId;

    try {
      // 1. Upload Manuscript
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title || 'Untitled Manuscript');
      formData.append('source_type', sourceType);
      formData.append('script', scriptInput);

      const uploadRes = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) throw new Error(`Upload failed with status ${uploadRes.status}`);

      const uploadData = await uploadRes.json();
      currentId = uploadData.id;
      setManuscriptId(currentId);

      // 2. Identify Script
      setIsIdentifying(true);
      const identifyFormData = new FormData();
      identifyFormData.append('manuscript_id', currentId);

      const identifyRes = await fetch(`${API_BASE}/identify-script`, {
        method: 'POST',
        body: identifyFormData,
      });

      if (!identifyRes.ok) throw new Error(`Script identification failed with status ${identifyRes.status}`);
      const identifyResult = await identifyRes.json();
      setScriptData(identifyResult);
      setIsIdentifying(false);

      // 3. Run Sarvam Document AI OCR
      setIsRunningOCR(true);
      const ocrFormData = new FormData();
      ocrFormData.append('manuscript_id', currentId);
      ocrFormData.append('script', identifyResult.script || scriptInput || 'Tamil');

      const ocrRes = await fetch(`${API_BASE}/ocr`, {
        method: 'POST',
        body: ocrFormData,
      });

      if (!ocrRes.ok) throw new Error(`OCR execution failed with status ${ocrRes.status}`);
      const ocrResult = await ocrRes.json();
      setOcrData(ocrResult);
      setIsRunningOCR(false);

      if (ocrResult.status === 'failed' || !ocrResult.extracted_text) {
        setOcrData(ocrResult);
        return; // Zero fallback rule: stop if OCR failed
      }

      // 4. Text Restoration
      setIsRestoring(true);
      const restoreFormData = new FormData();
      restoreFormData.append('manuscript_id', currentId);

      const restoreRes = await fetch(`${API_BASE}/restore`, {
        method: 'POST',
        body: restoreFormData,
      });

      if (!restoreRes.ok) throw new Error(`Restoration failed with status ${restoreRes.status}`);
      const restoreResult = await restoreRes.json();
      setRestorationData(restoreResult);
      setIsRestoring(false);

      if (restoreResult.status === 'failed' || !restoreResult.restored_text) {
        setRestorationError(restoreResult.message || 'OCR unavailable - manuscript was not processed');
        return;
      }

      // 5. Modern Tamil Conversion
      setIsConvertingModern(true);
      const modernFormData = new FormData();
      modernFormData.append('manuscript_id', currentId);

      const modernRes = await fetch(`${API_BASE}/convert-modern`, {
        method: 'POST',
        body: modernFormData,
      });

      if (!modernRes.ok) throw new Error(`Modern Tamil conversion failed with status ${modernRes.status}`);
      const modernResult = await modernRes.json();
      setModernTamilData(modernResult);
      setIsConvertingModern(false);

      if (modernResult.status === 'failed' || !modernResult.modern_tamil_text) {
        setModernError(modernResult.message || 'OCR unavailable - manuscript was not processed');
        return;
      }

      // 6. English Translation
      setIsTranslating(true);
      const translateFormData = new FormData();
      translateFormData.append('manuscript_id', currentId);

      const translateRes = await fetch(`${API_BASE}/translate-english`, {
        method: 'POST',
        body: translateFormData,
      });

      if (!translateRes.ok) throw new Error(`English translation failed with status ${translateRes.status}`);
      const translateResult = await translateRes.json();
      setTranslationData(translateResult);
      setIsTranslating(false);

      if (translateResult.status === 'failed' || !translateResult.english_translation) {
        setTranslationError(translateResult.message || 'Translation unavailable');
      }

    } catch (err) {
      console.error(err);
      setUploadError(err.message || 'An error occurred during manuscript analysis.');
    } finally {
      setIsUploading(false);
      setIsIdentifying(false);
      setIsRunningOCR(false);
      setIsRestoring(false);
      setIsConvertingModern(false);
      setIsTranslating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FDF8F0] text-[#2C1810] flex flex-col font-sans antialiased">
      
      {/* 1. NAVBAR */}
      <nav className="bg-[#2C1810] text-[#FDF8F0] border-b-4 border-[#D4AF37] shadow-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            
            {/* Logo & Branding */}
            <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('home')}>
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-[#8B3A2B] border-2 border-[#D4AF37] flex items-center justify-center font-bold text-xl sm:text-2xl text-[#D4AF37] shadow-inner font-serif-heading">
                ம
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xl sm:text-2xl font-black font-serif-heading tracking-wider text-[#D4AF37]">
                    MARUTHULIR
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-[#8B3A2B] text-[#FDF8F0] font-bold tracking-widest font-tamil">
                    மருதுளிர்
                  </span>
                </div>
                <p className="text-[10px] sm:text-xs text-amber-200/80 tracking-widest uppercase font-medium hidden sm:block">
                  Tamil Heritage Manuscript & Epigraphy System
                </p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <button
                onClick={() => setActiveTab('home')}
                className={`text-sm font-bold tracking-wide transition-colors ${
                  activeTab === 'home' ? 'text-[#D4AF37] border-b-2 border-[#D4AF37] pb-1' : 'text-[#FDF8F0]/80 hover:text-[#D4AF37]'
                }`}
              >
                {uiLanguage === 'en' ? 'Home' : 'முகப்பு'}
              </button>
              <button
                onClick={() => setActiveTab('explore')}
                className={`text-sm font-bold tracking-wide transition-colors ${
                  activeTab === 'explore' ? 'text-[#D4AF37] border-b-2 border-[#D4AF37] pb-1' : 'text-[#FDF8F0]/80 hover:text-[#D4AF37]'
                }`}
              >
                {uiLanguage === 'en' ? 'Explore Heritage' : 'பாரம்பரிய சுவடிகள்'}
              </button>
              <button
                onClick={() => setActiveTab('about')}
                className={`text-sm font-bold tracking-wide transition-colors ${
                  activeTab === 'about' ? 'text-[#D4AF37] border-b-2 border-[#D4AF37] pb-1' : 'text-[#FDF8F0]/80 hover:text-[#D4AF37]'
                }`}
              >
                {uiLanguage === 'en' ? 'About Project' : 'எங்களைப் பற்றி'}
              </button>
            </div>

            {/* Right Controls: UI Language Toggle & Action */}
            <div className="flex items-center space-x-3">
              {/* Language Toggle */}
              <button
                onClick={() => setUiLanguage(uiLanguage === 'en' ? 'ta' : 'en')}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#8B3A2B] border border-[#D4AF37]/50 text-xs font-bold text-[#FDF8F0] hover:border-[#D4AF37] transition-all shadow"
              >
                <Languages className="w-4 h-4 text-[#D4AF37]" />
                <span>{uiLanguage === 'en' ? 'தமிழ்' : 'English'}</span>
              </button>

              {(ocrData || restorationData) && (
                <button
                  onClick={handleDownloadReport}
                  className="hidden sm:flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-bold bg-[#D4AF37] hover:bg-[#c49f27] text-[#2C1810] rounded-lg transition-colors shadow"
                >
                  <Download className="w-4 h-4" />
                  <span>{uiLanguage === 'en' ? 'Export Report' : 'அறிக்கை தரவிறக்கு'}</span>
                </button>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 text-[#D4AF37] hover:text-white"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-[#2C1810] border-t border-[#D4AF37]/30 px-4 py-3 space-y-2">
            <button
              onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}
              className="block w-full text-left py-2 px-3 text-sm font-bold text-[#D4AF37] hover:bg-[#8B3A2B]/40 rounded"
            >
              Home / முகப்பு
            </button>
            <button
              onClick={() => { setActiveTab('explore'); setMobileMenuOpen(false); }}
              className="block w-full text-left py-2 px-3 text-sm font-bold text-[#FDF8F0] hover:bg-[#8B3A2B]/40 rounded"
            >
              Explore Heritage / சுவடிகள்
            </button>
            <button
              onClick={() => { setActiveTab('about'); setMobileMenuOpen(false); }}
              className="block w-full text-left py-2 px-3 text-sm font-bold text-[#FDF8F0] hover:bg-[#8B3A2B]/40 rounded"
            >
              About Project / எங்களைப் பற்றி
            </button>
          </div>
        )}
      </nav>

      {/* VIEW: EXPLORE HERITAGE */}
      {activeTab === 'explore' && (
        <div className="max-w-6xl mx-auto p-6 space-y-8 flex-grow animate-fadeIn">
          <div className="text-center space-y-3">
            <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-[#8B3A2B]/10 border border-[#8B3A2B]/30 text-[#8B3A2B] text-xs font-bold">
              <Compass className="w-4 h-4 text-[#D4AF37]" />
              <span>Tamil Epigraphy & Manuscript Traditions</span>
            </div>
            <h2 className="text-3xl font-black font-serif-heading text-[#8B3A2B]">
              Exploring Tamil Scripts Across Centuries
            </h2>
            <p className="text-sm text-[#2C1810]/80 max-w-2xl mx-auto">
              Tamil possesses one of the longest surviving epigraphical and literary traditions in Asia, documented across stone inscriptions (<span className="font-tamil font-semibold">கல்வெட்டு</span>) and palm-leaf manuscripts (<span className="font-tamil font-semibold">ஓலைச்சுவடி</span>).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
              <span className="px-2.5 py-1 bg-[#8B3A2B] text-[#D4AF37] font-bold text-xs rounded-full">3rd c. BCE – 3rd c. CE</span>
              <h3 className="text-xl font-bold text-[#8B3A2B] font-tamil">Tamil-Brahmi (தமிழ் பிராமி)</h3>
              <p className="text-xs text-[#2C1810]/80 leading-relaxed">
                Found in rock shelters, caverns, and pot-sherds across Tamil Nadu. Characterized by angular geometric strokes carved directly into granite surfaces.
              </p>
            </div>

            <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
              <span className="px-2.5 py-1 bg-[#8B3A2B] text-[#D4AF37] font-bold text-xs rounded-full">4th c. CE – 11th c. CE</span>
              <h3 className="text-xl font-bold text-[#8B3A2B] font-tamil">Vatteluttu (வட்டெழுத்து)</h3>
              <p className="text-xs text-[#2C1810]/80 leading-relaxed">
                Meaning 'rounded letters', developed for smooth scribing on dried Palmyra palm leaves without tearing the fragile plant fibers.
              </p>
            </div>

            <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
              <span className="px-2.5 py-1 bg-[#8B3A2B] text-[#D4AF37] font-bold text-xs rounded-full">6th c. CE – 19th c. CE</span>
              <h3 className="text-xl font-bold text-[#8B3A2B] font-tamil">Grantha Script (கிரந்தம்)</h3>
              <p className="text-xs text-[#2C1810]/80 leading-relaxed">
                Historically utilized in Southern India to transcribe Sanskrit terms and scientific treatises in Tamil palm-leaf collections.
              </p>
            </div>
          </div>

          <div className="text-center pt-4">
            <button
              onClick={() => setActiveTab('home')}
              className="bg-[#8B3A2B] hover:bg-[#722e22] text-[#FDF8F0] font-bold py-3 px-6 rounded-xl shadow border border-[#D4AF37] inline-flex items-center space-x-2 text-sm"
            >
              <span>Analyze Your Manuscript Image</span>
              <ArrowRight className="w-4 h-4 text-[#D4AF37]" />
            </button>
          </div>
        </div>
      )}

      {/* VIEW: ABOUT */}
      {activeTab === 'about' && (
        <div className="max-w-4xl mx-auto p-6 space-y-8 flex-grow animate-fadeIn">
          <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-8 shadow-sm space-y-6">
            <div className="flex items-center space-x-3 border-b border-[#D4AF37]/30 pb-4">
              <div className="w-12 h-12 rounded-full bg-[#8B3A2B] text-[#D4AF37] flex items-center justify-center font-bold text-2xl font-serif-heading">
                ம
              </div>
              <div>
                <h2 className="text-2xl font-bold font-serif-heading text-[#8B3A2B]">
                  About Maruthulir (மருதுளிர்) Project
                </h2>
                <p className="text-xs text-[#A0522D] font-semibold">
                  Preserving Classical Tamil Heritage through AI & Document Epigraphy
                </p>
              </div>
            </div>

            <p className="text-sm leading-relaxed text-[#2C1810]">
              <strong>Maruthulir</strong> (<span className="font-tamil">மருதுளிர்</span>) is an AI-powered restoration pipeline engineered to decipher ancient Tamil manuscripts, palm-leaf folios (ஓலைச்சுவடி), and stone epigraphy (கல்வெட்டு).
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 bg-[#FDF8F0] rounded-xl border border-[#D4AF37]/40 space-y-2">
                <h4 className="font-bold text-[#8B3A2B] text-sm flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                  <span>Sarvam Document AI OCR</span>
                </h4>
                <p className="text-xs text-[#2C1810]/80">
                  Leverages state-of-the-art Sarvam AI Document AI digitise engines tailored for Tamil language optical recognition.
                </p>
              </div>

              <div className="p-4 bg-[#FDF8F0] rounded-xl border border-[#D4AF37]/40 space-y-2">
                <h4 className="font-bold text-[#8B3A2B] text-sm flex items-center space-x-2">
                  <BookOpen className="w-4 h-4 text-[#8B3A2B]" />
                  <span>Linguistic Sandhi & Pulli Restoration</span>
                </h4>
                <p className="text-xs text-[#2C1810]/80">
                  Restores missing dots (புள்ளி), fixes word-final consonants, and normalizes classical sandhi (புணர்ச்சி விதி) rules.
                </p>
              </div>
            </div>

            <div className="text-center pt-4">
              <button
                onClick={() => setActiveTab('home')}
                className="bg-[#2C1810] hover:bg-[#3E251A] text-[#D4AF37] font-bold py-3 px-6 rounded-xl shadow-md border-2 border-[#D4AF37] inline-flex items-center space-x-2 text-sm"
              >
                <span>Back to Manuscript Analysis</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* VIEW: HOME (HERO + UPLOAD + PROCESSOR + RESULTS) */}
      {activeTab === 'home' && (
        <div className="flex-grow">
          
          {/* 2. HERO SECTION */}
          <section className="bg-gradient-to-b from-[#FAF3E0] via-[#FAF3E0]/80 to-[#FDF8F0] border-b border-[#D4AF37]/40 py-10 px-6">
            <div className="max-w-6xl mx-auto text-center space-y-4">
              
              <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-[#8B3A2B]/10 border border-[#8B3A2B]/30 text-[#8B3A2B] text-xs font-bold tracking-wide">
                <Award className="w-4 h-4 text-[#D4AF37]" />
                <span>AI-Powered Tamil Manuscript & Epigraphy Restoration System</span>
              </div>

              <h1 className="text-3xl sm:text-5xl font-black font-serif-heading text-[#8B3A2B] tracking-tight leading-tight">
                Preserving Ancient Tamil. <br className="hidden sm:inline" />
                Making Heritage Understandable.
              </h1>

              <p className="text-sm sm:text-base text-[#2C1810]/80 max-w-3xl mx-auto leading-relaxed">
                Discover the stories hidden in ancient Tamil manuscripts (<span className="font-tamil font-semibold">ஓலைச்சுவடி</span>) and stone inscriptions (<span className="font-tamil font-semibold">கல்வெட்டு</span>) using Sarvam AI OCR and Classical Tamil Linguistics.
              </p>

              {/* Heritage Visual Badges */}
              <div className="pt-2 flex flex-wrap items-center justify-center gap-2 text-xs font-semibold">
                <span className="px-3 py-1 bg-[#FDF8F0] border border-[#D4AF37] rounded-full text-[#8B3A2B]">
                  📜 Palm-Leaf (பனையோலை)
                </span>
                <span className="px-3 py-1 bg-[#FDF8F0] border border-[#D4AF37] rounded-full text-[#8B3A2B]">
                  🏛️ Stone Epigraphy (கல்வெட்டு)
                </span>
                <span className="px-3 py-1 bg-[#FDF8F0] border border-[#D4AF37] rounded-full text-[#8B3A2B]">
                  🔤 Vatteluttu & Brahmi Script Classifier
                </span>
                <span className="px-3 py-1 bg-[#FDF8F0] border border-[#D4AF37] rounded-full text-[#8B3A2B]">
                  🇮🇳 Sarvam AI Translation
                </span>
              </div>

              {/* 4. ANALYSIS PROGRESS BAR (7 Stages) */}
              <div className="pt-8 max-w-5xl mx-auto">
                <div className="text-xs font-bold text-[#8B3A2B] uppercase tracking-wider mb-2 text-left sm:text-center">
                  Live Processing Pipeline Stage ({currentStep}/7)
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-7 gap-2">
                  {[
                    { step: 1, label: '1. Upload', desc: 'File Ready' },
                    { step: 2, label: '2. Source ID', desc: 'Artifact Type' },
                    { step: 3, label: '3. Script ID', desc: 'Classifier' },
                    { step: 4, label: '4. Sarvam OCR', desc: 'Doc-AI Vision' },
                    { step: 5, label: '5. Restoration', desc: 'Sandhi/Pulli' },
                    { step: 6, label: '6. Modern Tamil', desc: 'Prose Conversion' },
                    { step: 7, label: '7. English', desc: 'AI Translation' },
                  ].map((s) => {
                    const isActive = currentStep === s.step;
                    const isCompleted = currentStep > s.step;
                    return (
                      <div
                        key={s.step}
                        className={`p-2 rounded-xl border text-center transition-all ${
                          isCompleted
                            ? 'bg-[#8B3A2B] text-[#FDF8F0] border-[#D4AF37]'
                            : isActive
                            ? 'bg-[#FAF3E0] text-[#8B3A2B] border-[#8B3A2B] border-2 shadow-md ring-2 ring-[#D4AF37]/50'
                            : 'bg-[#FDF8F0] text-[#2C1810]/50 border-[#D4AF37]/30'
                        }`}
                      >
                        <div className="text-[10px] font-bold uppercase tracking-wider">{s.label}</div>
                        <div className="text-[9px] opacity-80">{s.desc}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

            </div>
          </section>

          {/* MAIN WORKSPACE 2-COLUMN GRID */}
          <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* LEFT COLUMN (5 COLS): 3. UPLOAD SECTION & MANUSCRIPT PREVIEW */}
            <div className="lg:col-span-5 space-y-6">

              {/* Upload Card */}
              <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-3">
                  <h3 className="text-lg font-bold font-serif-heading text-[#8B3A2B] flex items-center space-x-2">
                    <Upload className="w-5 h-5 text-[#8B3A2B]" />
                    <span>Upload Manuscript Image</span>
                  </h3>
                  <span className="text-[11px] font-semibold text-[#A0522D] bg-[#FDF8F0] px-2 py-0.5 rounded border border-[#D4AF37]/40">
                    Step 1 of 7
                  </span>
                </div>

                <form onSubmit={handleRunFullPipeline} className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-[#2C1810] mb-1">
                      Manuscript Title
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Thirukkural Palm Leaf Folio #01"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      className="w-full bg-[#FDF8F0] border border-[#A0522D]/30 rounded-xl px-3.5 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-[#2C1810] mb-1">
                        Source Artifact Type
                      </label>
                      <select
                        value={sourceType}
                        onChange={(e) => setSourceType(e.target.value)}
                        className="w-full bg-[#FDF8F0] border border-[#A0522D]/30 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]"
                      >
                        <option value="palm-leaf">Palm-Leaf (பனையோலை)</option>
                        <option value="stone-inscription">Stone Inscription (கல்வெட்டு)</option>
                        <option value="copper-plate">Copper Plate (செப்பேடு)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-bold uppercase tracking-wider text-[#2C1810] mb-1">
                        Expected Script
                      </label>
                      <select
                        value={scriptInput}
                        onChange={(e) => setScriptInput(e.target.value)}
                        className="w-full bg-[#FDF8F0] border border-[#A0522D]/30 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#D4AF37]"
                      >
                        <option value="Tamil">Tamil (தமிழ்)</option>
                        <option value="Vatteluttu">Vatteluttu (வட்டெழுத்து)</option>
                        <option value="Tamil-Brahmi">Tamil-Brahmi (தமிழ் பிராமி)</option>
                        <option value="Grantha">Grantha (கிரந்தம்)</option>
                      </select>
                    </div>
                  </div>

                  {/* Upload Drag & Drop Zone */}
                  <div className="border-2 border-dashed border-[#A0522D]/40 rounded-xl p-6 text-center bg-[#FDF8F0] hover:border-[#D4AF37] transition-all cursor-pointer relative group">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="w-12 h-12 rounded-full bg-[#8B3A2B]/10 flex items-center justify-center text-[#8B3A2B] group-hover:scale-110 transition-transform">
                        <ImageIcon className="w-6 h-6" />
                      </div>
                      <p className="text-sm font-bold text-[#2C1810]">
                        {selectedFile ? selectedFile.name : 'Click to Browse or Drag Image Here'}
                      </p>
                      <p className="text-xs text-[#A0522D]">Supports JPG, PNG, WEBP manuscript formats</p>
                    </div>
                  </div>

                  {uploadError && (
                    <div className="flex items-center space-x-2 text-xs text-red-700 bg-red-50 p-3 rounded-xl border border-red-200 font-semibold">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>{uploadError}</span>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={isUploading || isIdentifying || isRunningOCR || isRestoring || isConvertingModern || isTranslating || !selectedFile}
                    className="w-full bg-[#8B3A2B] hover:bg-[#722e22] text-[#FDF8F0] font-bold py-3 px-4 rounded-xl shadow border border-[#D4AF37] flex items-center justify-center space-x-2 disabled:opacity-50 transition-all text-sm"
                  >
                    {(isUploading || isIdentifying || isRunningOCR || isRestoring || isConvertingModern || isTranslating) ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin text-[#D4AF37]" />
                        <span>Processing Pipeline Stage...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                        <span>Analyze Manuscript Now</span>
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Manuscript Preview Card */}
              {imagePreview && (
                <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-4 shadow-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[#8B3A2B]">
                      Uploaded Manuscript Image Preview
                    </h4>
                    {manuscriptId && (
                      <span className="text-[10px] bg-[#8B3A2B] text-[#D4AF37] px-2 py-0.5 rounded font-mono font-bold">
                        Record ID #{manuscriptId}
                      </span>
                    )}
                  </div>
                  <div className="rounded-xl overflow-hidden border border-[#A0522D]/30 bg-black/5 flex items-center justify-center p-2 min-h-[180px]">
                    <img
                      src={imagePreview}
                      alt="Manuscript Preview"
                      className="max-h-64 object-contain rounded"
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs text-[#A0522D]">
                    <span>Source: <strong>{sourceType}</strong></span>
                    <button
                      onClick={handleReset}
                      className="text-xs font-bold text-[#8B3A2B] hover:underline flex items-center space-x-1"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Analyze Another Image</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN (7 COLS): 5. RESULTS DASHBOARD (CARD 1-4) */}
            <div className="lg:col-span-7 space-y-6">

              {/* Detected Script & Artifact Summary Header */}
              <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold font-serif-heading text-[#8B3A2B] flex items-center space-x-2">
                    <Sparkles className="w-5 h-5 text-[#D4AF37]" />
                    <span>Script & Artifact Analysis</span>
                  </h3>
                  {scriptData && (
                    <span className="px-3 py-1 bg-[#8B3A2B] text-[#D4AF37] font-bold text-xs rounded-full border border-[#D4AF37]/40">
                      Confidence: {(scriptData.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>

                {scriptData ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-4 bg-[#FDF8F0] p-4 rounded-xl border border-[#D4AF37]/40">
                      <div>
                        <span className="text-[10px] text-[#A0522D] font-bold uppercase tracking-wider block">
                          Identified Script
                        </span>
                        <span className="text-xl font-bold text-[#8B3A2B] font-tamil">
                          {scriptData.script}
                        </span>
                      </div>
                      <div>
                        <span className="text-[10px] text-[#A0522D] font-bold uppercase tracking-wider block">
                          Artifact Source
                        </span>
                        <span className="text-base font-bold text-[#2C1810] capitalize">
                          {sourceType.replace('-', ' ')}
                        </span>
                      </div>
                    </div>

                    <div className="p-3 bg-[#FDF8F0] rounded-xl border border-[#A0522D]/20 text-xs text-[#2C1810]">
                      <span className="font-bold text-[#8B3A2B] block mb-1">Classifier Rationale:</span>
                      <p>{scriptData.explanation}</p>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 text-center border-2 border-dashed border-[#A0522D]/20 rounded-xl bg-[#FDF8F0]">
                    <p className="text-sm text-[#A0522D]">
                      Upload a manuscript image to view automated script classification and Sarvam OCR results.
                    </p>
                  </div>
                )}
              </div>

              {/* CARD 1: Raw OCR Result */}
              <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
                <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-[#8B3A2B] text-[#FDF8F0] font-bold text-xs flex items-center justify-center font-mono">
                      1
                    </span>
                    <h4 className="text-base font-bold font-serif-heading text-[#8B3A2B]">
                      Raw OCR Output (மூல ஓசிஆர் உரை)
                    </h4>
                  </div>

                  {ocrData?.extracted_text && (
                    <button
                      onClick={() => handleCopy(ocrData.extracted_text, 'ocr')}
                      className="flex items-center space-x-1 text-xs text-[#8B3A2B] hover:text-[#2C1810] bg-[#FDF8F0] px-2.5 py-1 rounded-lg border border-[#A0522D]/30 font-semibold"
                    >
                      {copiedCard === 'ocr' ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCard === 'ocr' ? 'Copied!' : 'Copy'}</span>
                    </button>
                  )}
                </div>

                {isRunningOCR ? (
                  <div className="p-6 bg-[#FDF8F0] rounded-xl border border-dashed border-[#D4AF37] text-center space-y-2">
                    <RefreshCw className="w-6 h-6 animate-spin text-[#8B3A2B] mx-auto" />
                    <span className="text-xs font-bold text-[#8B3A2B]">Executing Sarvam Document AI OCR...</span>
                  </div>
                ) : ocrData ? (
                  <div className="space-y-3">
                    {ocrData.status === 'completed' && ocrData.extracted_text ? (
                      <>
                        <div className="flex items-center justify-between text-xs px-3 py-1.5 bg-green-50 text-green-800 rounded-lg border border-green-200">
                          <span className="flex items-center space-x-1 font-semibold">
                            <CheckCircle className="w-3.5 h-3.5 text-green-600" />
                            <span>Sarvam Document AI OCR Executed</span>
                          </span>
                          <span className="font-bold">
                            Confidence: {ocrData.confidence !== null && ocrData.confidence !== undefined ? (ocrData.confidence * 100).toFixed(0) + '%' : 'N/A'}
                          </span>
                        </div>
                        <div className="p-4 bg-[#FDF8F0] border-2 border-[#D4AF37] rounded-xl font-tamil text-base leading-relaxed text-[#2C1810] whitespace-pre-wrap min-h-[80px] shadow-inner">
                          {ocrData.extracted_text}
                        </div>
                      </>
                    ) : (
                      <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 space-y-1">
                        <div className="flex items-center space-x-2 font-bold">
                          <ShieldAlert className="w-4 h-4 text-red-600 flex-shrink-0" />
                          <span>{ocrData.message || 'OCR unavailable - manuscript was not processed'}</span>
                        </div>
                        <p className="text-[11px] text-red-700">
                          Downstream restoration and translation steps are blocked because no text was extracted.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-6 text-center border-2 border-dashed border-[#A0522D]/20 rounded-xl bg-[#FDF8F0] text-xs text-[#A0522D]">
                    Raw OCR output will be displayed here once OCR completes.
                  </div>
                )}
              </div>

              {/* CARD 2: Restored Classical Tamil */}
              <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
                <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-[#8B3A2B] text-[#FDF8F0] font-bold text-xs flex items-center justify-center font-mono">
                      2
                    </span>
                    <h4 className="text-base font-bold font-serif-heading text-[#8B3A2B]">
                      Restored Classical Tamil (சீரமைக்கப்பட்ட உரை)
                    </h4>
                  </div>

                  {restorationData?.restored_text && (
                    <button
                      onClick={() => handleCopy(restorationData.restored_text, 'restoration')}
                      className="flex items-center space-x-1 text-xs text-[#8B3A2B] hover:text-[#2C1810] bg-[#FDF8F0] px-2.5 py-1 rounded-lg border border-[#A0522D]/30 font-semibold"
                    >
                      {copiedCard === 'restoration' ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCard === 'restoration' ? 'Copied!' : 'Copy'}</span>
                    </button>
                  )}
                </div>

                {restorationError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 font-bold flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{restorationError}</span>
                  </div>
                )}

                {isRestoring ? (
                  <div className="p-6 bg-[#FDF8F0] rounded-xl border border-dashed border-[#D4AF37] text-center space-y-2">
                    <RefreshCw className="w-6 h-6 animate-spin text-[#8B3A2B] mx-auto" />
                    <span className="text-xs font-bold text-[#8B3A2B]">Restoring Classical Sandhi & Pulli Dots...</span>
                  </div>
                ) : restorationData?.restored_text ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-xs px-3 py-1.5 bg-[#FDF8F0] rounded-lg border border-[#D4AF37]/40">
                      <span className="text-[#A0522D] font-bold">Rule-based Heritage Restorer</span>
                      <span className="font-bold text-[#8B3A2B]">
                        Confidence: {(restorationData.confidence * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="p-4 bg-[#FDF8F0] border-2 border-[#D4AF37] rounded-xl font-tamil text-base leading-relaxed text-[#2C1810] whitespace-pre-wrap font-semibold min-h-[80px] shadow-sm">
                      {restorationData.restored_text}
                    </div>

                    {/* Corrections Breakdown */}
                    {restorationData.corrections && restorationData.corrections.length > 0 && (
                      <div className="pt-2 space-y-1.5">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-[#8B3A2B] block">
                          Restoration Rationale & Corrections ({restorationData.corrections.length})
                        </span>
                        <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                          {restorationData.corrections.map((corr, idx) => (
                            <div key={idx} className="p-2 bg-[#FDF8F0] rounded-lg border border-[#A0522D]/20 text-xs flex justify-between items-start">
                              <div>
                                <span className="font-tamil font-bold text-[#8B3A2B]">
                                  <span className="line-through text-red-600 mr-1">{corr.original}</span> → <span className="text-green-700">{corr.corrected}</span>
                                </span>
                                <p className="text-[11px] text-[#2C1810]/70 mt-0.5">{corr.explanation}</p>
                              </div>
                              <span className="text-[10px] bg-[#8B3A2B]/10 text-[#8B3A2B] font-bold px-1.5 py-0.5 rounded">
                                {(corr.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-6 text-center border-2 border-dashed border-[#A0522D]/20 rounded-xl bg-[#FDF8F0] text-xs text-[#A0522D]">
                    Restored Classical Tamil text will appear here after restoration step.
                  </div>
                )}
              </div>

              {/* CARD 3: Modern Tamil Prose */}
              <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
                <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-[#8B3A2B] text-[#FDF8F0] font-bold text-xs flex items-center justify-center font-mono">
                      3
                    </span>
                    <h4 className="text-base font-bold font-serif-heading text-[#8B3A2B]">
                      Modern Tamil Prose (தற்கால எளிய உரை)
                    </h4>
                  </div>

                  {modernTamilData?.modern_tamil_text && (
                    <button
                      onClick={() => handleCopy(modernTamilData.modern_tamil_text, 'modern')}
                      className="flex items-center space-x-1 text-xs text-[#8B3A2B] hover:text-[#2C1810] bg-[#FDF8F0] px-2.5 py-1 rounded-lg border border-[#A0522D]/30 font-semibold"
                    >
                      {copiedCard === 'modern' ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCard === 'modern' ? 'Copied!' : 'Copy'}</span>
                    </button>
                  )}
                </div>

                {modernError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 font-bold flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{modernError}</span>
                  </div>
                )}

                {isConvertingModern ? (
                  <div className="p-6 bg-[#FDF8F0] rounded-xl border border-dashed border-green-600/40 text-center space-y-2">
                    <RefreshCw className="w-6 h-6 animate-spin text-green-700 mx-auto" />
                    <span className="text-xs font-bold text-green-800">Converting to Modern Tamil Prose...</span>
                  </div>
                ) : modernTamilData?.modern_tamil_text ? (
                  <div className="p-4 bg-[#FDF8F0] border-2 border-green-700/60 rounded-xl font-tamil text-base leading-relaxed text-green-950 font-medium min-h-[80px] shadow-sm">
                    {modernTamilData.modern_tamil_text}
                  </div>
                ) : (
                  <div className="p-6 text-center border-2 border-dashed border-[#A0522D]/20 rounded-xl bg-[#FDF8F0] text-xs text-[#A0522D]">
                    Modern Tamil prose translation will appear here once converted.
                  </div>
                )}
              </div>

              {/* CARD 4: English Translation */}
              <div className="bg-[#FAF3E0] border-2 border-[#D4AF37]/50 rounded-2xl p-6 shadow-sm space-y-3">
                <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-3">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-[#8B3A2B] text-[#FDF8F0] font-bold text-xs flex items-center justify-center font-mono">
                      4
                    </span>
                    <h4 className="text-base font-bold font-serif-heading text-[#8B3A2B]">
                      English Translation
                    </h4>
                  </div>

                  {translationData?.english_translation && (
                    <button
                      onClick={() => handleCopy(translationData.english_translation, 'english')}
                      className="flex items-center space-x-1 text-xs text-[#8B3A2B] hover:text-[#2C1810] bg-[#FDF8F0] px-2.5 py-1 rounded-lg border border-[#A0522D]/30 font-semibold"
                    >
                      {copiedCard === 'english' ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCard === 'english' ? 'Copied!' : 'Copy'}</span>
                    </button>
                  )}
                </div>

                {translationError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-800 font-bold flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{translationError}</span>
                  </div>
                )}

                {isTranslating ? (
                  <div className="p-6 bg-[#FDF8F0] rounded-xl border border-dashed border-blue-600/40 text-center space-y-2">
                    <RefreshCw className="w-6 h-6 animate-spin text-blue-800 mx-auto" />
                    <span className="text-xs font-bold text-blue-900">Translating to English via Sarvam AI...</span>
                  </div>
                ) : translationData?.english_translation ? (
                  <div className="space-y-3">
                    <div className="p-4 bg-[#FDF8F0] border-2 border-blue-700/60 rounded-xl text-base leading-relaxed text-blue-950 font-medium min-h-[80px] shadow-sm">
                      {translationData.english_translation}
                    </div>

                    {/* AI Disclaimer Badge */}
                    <div className="flex items-center space-x-2 text-[11px] text-[#A0522D] bg-[#FDF8F0] p-2.5 rounded-lg border border-[#D4AF37]/40">
                      <Info className="w-4 h-4 text-[#D4AF37] flex-shrink-0" />
                      <span>
                        <strong>AI Disclaimer:</strong> AI-generated translation for historical research. Verify epigraphical details with domain specialists.
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 text-center border-2 border-dashed border-[#A0522D]/20 rounded-xl bg-[#FDF8F0] text-xs text-[#A0522D]">
                    English translation will appear here after modern Tamil conversion.
                  </div>
                )}
              </div>

            </div>
          </main>
        </div>
      )}

      {/* FOOTER */}
      <footer className="bg-[#2C1810] text-[#FDF8F0] border-t-2 border-[#D4AF37] py-8 px-6 text-center text-xs space-y-2 mt-auto">
        <p className="font-serif-heading font-bold text-[#D4AF37] text-base tracking-wider">
          MARUTHULIR (மருதுளிர்) — TAMIL HERITAGE RESTORATION SYSTEM
        </p>
        <p className="text-amber-200/70 max-w-xl mx-auto">
          Preserving Epigraphic Heritage & Manuscript Wisdom via Sarvam AI & Classical Tamil Linguistics.
        </p>
        <div className="pt-2 text-[10px] text-[#FDF8F0]/40">
          Built for Hackathon Demonstration • FastAPI + PostgreSQL + React + Vite + Sarvam Document AI
        </div>
      </footer>
    </div>
  );
}
