import React, { useState, useRef } from 'react';
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
  Languages,
  Check,
  Menu,
  X,
  ArrowRight,
  Eye,
  Archive,
  Search,
  CheckSquare,
  Edit3,
  Layers,
  Award,
  Scroll,
  ShieldCheck
} from 'lucide-react';

const API_BASE = typeof window !== 'undefined'
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : 'http://127.0.0.1:8000';

export default function App() {
  // Navigation & Language State
  const [activeTab, setActiveTab] = useState('home'); // 'home' | 'digitize' | 'archive' | 'about'
  const [uiLanguage, setUiLanguage] = useState('en'); // 'en' | 'ta'
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [viewOriginalModal, setViewOriginalModal] = useState(false);

  // Upload Form State
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState('palm-leaf'); // 'palm-leaf' | 'stone-inscription'
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

  // Scholar Review State
  const [editableClassicalTamil, setEditableClassicalTamil] = useState('');
  const [isScholarApproved, setIsScholarApproved] = useState(false);

  // Final Output Data States
  const [modernTamilData, setModernTamilData] = useState(null);
  const [isConvertingModern, setIsConvertingModern] = useState(false);

  const [translationData, setTranslationData] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);

  // Feedback State
  const [copiedCard, setCopiedCard] = useState(null);

  // File Ref
  const fileInputRef = useRef(null);

  // UI Strings
  const strings = {
    en: {
      appName: 'MARUTHULIR',
      appTamilName: 'மருதுளிர்',
      subtitle: 'Tamil Manuscripts & Epigraphy Restoration Platform',
      navHome: 'Home',
      navDigitize: 'Digitize & Restore',
      navArchive: 'Archival Catalog',
      navAbout: 'About Platform',
      ctaStartDigitizing: 'Start Restoration',
      heroTitle: 'Tamil Heritage Manuscript & Epigraphy Restoration',
      heroSubtitle: 'Preserving ancient Tamil palm-leaf manuscripts and stone inscriptions through Sarvam OCR, Reference Lexicon candidate retrieval, and Scholar-Approved Modernization.',
      selectSourceType: 'Select Artifact Source Type',
      sourcePalmLeaf: 'Palm-Leaf Manuscript',
      sourcePalmLeafDesc: 'Classical Olai Chuvadi (ஓலைச்சுவடி) — faded ink, scribal wear, leaf margin damage',
      sourceStoneInscription: 'Stone Inscription',
      sourceStoneInscriptionDesc: 'Temple & Epigraphic Stone Carvings (கல்வெட்டு) — weathered surface, carved erosion',
      uploadTitle: 'Upload Artifact Image',
      uploadDragText: 'Drag & drop palm-leaf manuscript or stone inscription image',
      uploadChooseText: 'or browse from your system',
      uploadFormats: 'Supports PNG, JPG, JPEG, WEBP up to 20MB',
      inputTitleLabel: 'Artifact Title (Optional)',
      inputTitlePlaceholder: 'e.g. Tanjavur Temple Inscription Strip / Thirukkural Leaf 12',
      btnRunPipeline: 'Execute AI Analysis & Restoration',
      pipelineTitle: 'Digitization Pipeline Status',
      stepUpload: 'Image Upload',
      stepIdentify: 'Script Identification',
      stepOcr: 'Sarvam OCR',
      stepRestore: 'Candidate Restoration',
      stepReview: 'Scholar Review',
      stepResults: 'Modern Results',
      scholarReviewTitle: 'Scholar Review & Approval Stage',
      scholarReviewSubtitle: 'Review damage evidence, candidate suggestions, and approve the restored Classical Tamil text before generating student modern Tamil & translation.',
      approvedClassicalLabel: 'Scholar-Approved Classical Tamil Text',
      btnApproveAndContinue: 'Approve Classical Tamil & Generate Final Outputs',
      card1Title: 'Scholar-Approved Classical Tamil',
      card2Title: 'Modern Readable Tamil (For Students)',
      card2Subtitle: 'Single natural, fluent contemporary Tamil paragraph for school & college students (தற்கால எளிய உரை)',
      card3Title: 'English Translation',
      card3Subtitle: 'Natural English translation of the scholar-approved historical text',
      sourceTypeLabel: 'Source Type:',
      copyText: 'Copy Text',
      copied: 'Copied!',
      downloadReport: 'Export Archival Report'
    },
    ta: {
      appName: 'மருதுளிர்',
      appTamilName: 'MARUTHULIR',
      subtitle: 'தமிழ் ஏட்டுச்சுவடி & கல்வெட்டு சீரமைப்பு தளம்',
      navHome: 'முகப்பு',
      navDigitize: 'டிஜிட்டல் மயமாக்குக',
      navArchive: 'ஆவணக் காப்பகம்',
      navAbout: 'தளத்தைப் பற்றி',
      ctaStartDigitizing: 'சீரமைப்பைத் தொடங்கு',
      heroTitle: 'தமிழ் ஏட்டுச்சுவடி & கல்வெட்டு மறுசீரமைப்பு தளம்',
      heroSubtitle: 'பண்டைய தமிழ் ஓலைச்சுவடிகள் மற்றும் திருக்கோயில் கல்வெட்டுகளை சர்வம் OCR, சங்க இலக்கிய சொற்களஞ்சியம் மற்றும் வல்லுநர் சரிபார்ப்பு மூலம் பாதுகாத்தல்.',
      selectSourceType: 'ஆவண வகையைத் தேர்ந்தெடுக்கவும்',
      sourcePalmLeaf: 'ஓலைச்சுவடி',
      sourcePalmLeafDesc: 'பண்டைய தமிழ் ஓலைச்சுவடிகள் (Olai Chuvadi) — மங்கிய மை, ஏட்டுச் சிதைவு',
      sourceStoneInscription: 'கல்வெட்டு',
      sourceStoneInscriptionDesc: 'கோயில் கற்பொறிப்புகள் & கல்வெட்டுகள் (Epigraphy) — தேய்ந்த எழுத்துகள், கல் அரிப்பு',
      uploadTitle: 'ஆவணப் படத்தை பதிவேற்றவும்',
      uploadDragText: 'ஓலைச்சுவடி அல்லது கல்வெட்டு படத்தை இழுத்து விடவும்',
      uploadChooseText: 'அல்லது கணினியிலிருந்து தேர்வு செய்யவும்',
      uploadFormats: 'PNG, JPG, JPEG, WEBP (அதிகபட்சம் 20MB)',
      inputTitleLabel: 'ஆவணத் தலைப்பு (விருப்பத்தேர்வு)',
      inputTitlePlaceholder: 'எ.கா. தஞ்சைக் கோயில் கல்வெட்டு தொகுதி 1',
      btnRunPipeline: 'AI பகுப்பாய்வு & சீரமைப்பைத் தொடங்கு',
      pipelineTitle: 'பகுப்பாய்வு முன்னேற்றம்',
      stepUpload: 'படம் பதிவேற்றம்',
      stepIdentify: 'எழுத்து அறிதல்',
      stepOcr: 'சர்வம் OCR',
      stepRestore: 'உரை சீரமைப்பு',
      stepReview: 'வல்லுநர் சரிபார்ப்பு',
      stepResults: 'முடிவுகள்',
      scholarReviewTitle: 'வல்லுநர் சரிபார்ப்பு & ஒப்புதல் நிலை',
      scholarReviewSubtitle: 'சேத விவரங்கள் மற்றும் அகராதி பரிந்துரைகளை ஆய்வு செய்து, சீரமைக்கப்பட்ட பண்டைய தமிழ் உரையை உறுதிப்படுத்தவும்.',
      approvedClassicalLabel: 'வல்லுநரால் உறுதிசெய்யப்பட்ட பண்டைய தமிழ் உரை',
      btnApproveAndContinue: 'பண்டைய தமிழை உறுதிசெய்து தற்கால உரை பெறுக',
      card1Title: 'உறுதிசெய்யப்பட்ட பண்டைய தமிழ் உரை',
      card2Title: 'தற்கால எளிய தமிழ் (மாணவர் உரை)',
      card2Subtitle: 'பண்டைய உரை கருத்தை விளக்கும் தற்கால எளிய தமிழ் பத்தி (தற்கால எளிய உரை)',
      card3Title: 'ஆங்கில மொழிபெயர்ப்பு',
      card3Subtitle: 'வரலாற்று உரையின் இயற்கை ஆங்கில மொழிபெயர்ப்பு',
      sourceTypeLabel: 'ஆவண வகை:',
      copyText: 'உரையை நகலெடு',
      copied: 'நகலெடுக்கப்பட்டது!',
      downloadReport: 'ஆவண அறிக்கை பெறுக'
    }
  };

  const t = strings[uiLanguage];

  // Pipeline Step Counter (0..5)
  const currentStep = (() => {
    if (isScholarApproved && modernTamilData) return 5;
    if (restorationData) return 4;
    if (ocrData?.extracted_text) return 3;
    if (scriptData) return 2;
    if (manuscriptId) return 1;
    if (selectedFile) return 0;
    return 0;
  })();

  // Reset State
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
    setEditableClassicalTamil('');
    setIsScholarApproved(false);
    setModernTamilData(null);
    setIsConvertingModern(false);
    setTranslationData(null);
    setIsTranslating(false);
  };

  // Copy helper
  const handleCopy = (text, cardName) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedCard(cardName);
    setTimeout(() => setCopiedCard(null), 2000);
  };

  // File Change
  const handleFileChange = (e) => {
    const file = e.target.files ? e.target.files[0] : null;
    if (file) {
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setUploadError('');
      setManuscriptId(null);
      setScriptData(null);
      setOcrData(null);
      setRestorationData(null);
      setIsScholarApproved(false);
      setEditableClassicalTamil('');
      setModernTamilData(null);
      setTranslationData(null);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setUploadError('');
      setManuscriptId(null);
      setScriptData(null);
      setOcrData(null);
      setRestorationData(null);
      setIsScholarApproved(false);
      setEditableClassicalTamil('');
      setModernTamilData(null);
      setTranslationData(null);
      if (!title) {
        setTitle(file.name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  // Run initial AI analysis (Upload -> Script Identify -> Sarvam OCR -> Restoration Candidates)
  const handleRunPipeline = async (e) => {
    if (e) e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select an artifact image file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadError('');
    setScriptData(null);
    setOcrData(null);
    setRestorationData(null);
    setRestorationError('');
    setIsScholarApproved(false);
    setEditableClassicalTamil('');
    setModernTamilData(null);
    setTranslationData(null);

    let currentId = manuscriptId;

    try {
      // 1. Upload Artifact
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title || 'Untitled Artifact');
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
      setIsUploading(false);

      // 2. Identify Script & Source Characteristics
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

      // 3. Execute Sarvam OCR
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
        setUploadError(ocrResult.message || 'OCR processing failed to extract text from manuscript image.');
        return;
      }

      // 4. Generate Candidate Restoration & Damage Evidence
      setIsRestoring(true);
      const restoreFormData = new FormData();
      restoreFormData.append('manuscript_id', currentId);
      restoreFormData.append('source_type', sourceType);

      const restoreRes = await fetch(`${API_BASE}/restore`, {
        method: 'POST',
        body: restoreFormData,
      });

      if (!restoreRes.ok) throw new Error(`Restoration failed with status ${restoreRes.status}`);
      const restoreResult = await restoreRes.json();
      setRestorationData(restoreResult);
      const rawRestored = (restoreResult.restored_text || '').replace(/<restored Tamil text>/g, '').trim();
      const validRestored = (rawRestored && !rawRestored.includes('restored Tamil text')) ? rawRestored : (ocrResult.extracted_text || '');
      setEditableClassicalTamil(validRestored);
      setIsRestoring(false);

      // Smooth scroll down to Scholar Review section
      setTimeout(() => {
        const el = document.getElementById('scholar-review-section');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);

    } catch (err) {
      console.error(err);
      setUploadError(err.message || 'An error occurred during artifact analysis.');
    } finally {
      setIsUploading(false);
      setIsIdentifying(false);
      setIsRunningOCR(false);
      setIsRestoring(false);
    }
  };

  // Scholar Review Approval Event Handler
  const handleApproveScholarReview = async () => {
    const textToApprove = (editableClassicalTamil || '').trim();
    if (!textToApprove) return;

    setIsConvertingModern(true);
    setIsTranslating(true);

    try {
      const formData = new FormData();
      if (manuscriptId) {
        formData.append('manuscript_id', manuscriptId);
      }
      formData.append('approved_text', textToApprove);

      const reviewRes = await fetch(`${API_BASE}/scholar-review`, {
        method: 'POST',
        body: formData,
      });

      if (!reviewRes.ok) throw new Error(`Scholar review approval failed with status ${reviewRes.status}`);
      const reviewResult = await reviewRes.json();

      setModernTamilData({
        modern_tamil_text: reviewResult.modern_tamil_text,
        status: reviewResult.status
      });
      setTranslationData({
        english_translation: reviewResult.english_translation,
        status: reviewResult.status
      });
      setIsScholarApproved(true);

      // Smooth scroll down to final results section
      setTimeout(() => {
        const el = document.getElementById('final-results-section');
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 100);

    } catch (err) {
      console.error(err);
      alert('Failed to process scholar approval: ' + err.message);
    } finally {
      setIsConvertingModern(false);
      setIsTranslating(false);
    }
  };

  const scrollToSection = (id) => {
    setActiveTab(id);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const getSourceTypeDisplay = () => {
    if (sourceType === 'stone-inscription' || sourceType === 'inscription') {
      return {
        label: 'Stone Inscription',
        tamilLabel: 'கல்வெட்டு',
        badgeBg: 'bg-amber-950/40 border-amber-500/50 text-amber-300',
        icon: <Scroll className="w-4 h-4 text-amber-400" />
      };
    }
    return {
      label: 'Palm-leaf Manuscript',
      tamilLabel: 'ஓலைச்சுவடி',
      badgeBg: 'bg-teal-950/40 border-teal-500/50 text-teal-300',
      icon: <BookOpen className="w-4 h-4 text-teal-400" />
    };
  };

  const stDisplay = getSourceTypeDisplay();

  return (
    <div className="min-h-screen bg-[#0D0B08] text-[#E8DCC4] flex flex-col font-sans selection:bg-[#D4AF37]/30 selection:text-[#FFF8E7]">
      
      {/* NAVBAR */}
      <nav className="bg-[#120E0A]/95 backdrop-blur-md border-b border-[#D4AF37]/30 sticky top-0 z-50 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            
            <div 
              className="flex items-center space-x-3.5 cursor-pointer group" 
              onClick={() => scrollToSection('home')}
            >
              <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-[#2D2116] to-[#16100B] border border-[#D4AF37]/60 flex items-center justify-center shadow-lg group-hover:border-[#D4AF37] transition-all">
                <span className="font-tamil-serif font-bold text-2xl text-[#E6C280] drop-shadow-md">
                  ம
                </span>
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xl sm:text-2xl font-black font-serif-heading tracking-wider gold-gradient-text">
                    மருதுளிர்
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-[#D4AF37]/15 text-[#E6C280] font-semibold border border-[#D4AF37]/30 tracking-widest hidden sm:inline-block">
                    MARUTHULIR
                  </span>
                </div>
                <p className="text-[10px] sm:text-xs text-[#A09382] tracking-widest uppercase font-medium">
                  {t.subtitle}
                </p>
              </div>
            </div>

            <div className="hidden md:flex items-center space-x-8">
              <button
                onClick={() => scrollToSection('home')}
                className={`text-sm font-semibold tracking-wide transition-all ${
                  activeTab === 'home' ? 'text-[#E6C280] border-b-2 border-[#D4AF37] pb-1' : 'text-[#A09382] hover:text-[#E8DCC4]'
                }`}
              >
                {t.navHome}
              </button>
              <button
                onClick={() => scrollToSection('digitize')}
                className={`text-sm font-semibold tracking-wide transition-all ${
                  activeTab === 'digitize' ? 'text-[#E6C280] border-b-2 border-[#D4AF37] pb-1' : 'text-[#A09382] hover:text-[#E8DCC4]'
                }`}
              >
                {t.navDigitize}
              </button>
              <button
                onClick={() => scrollToSection('archive')}
                className={`text-sm font-semibold tracking-wide transition-all ${
                  activeTab === 'archive' ? 'text-[#E6C280] border-b-2 border-[#D4AF37] pb-1' : 'text-[#A09382] hover:text-[#E8DCC4]'
                }`}
              >
                {t.navArchive}
              </button>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setUiLanguage(uiLanguage === 'en' ? 'ta' : 'en')}
                className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-[#1A140F] border border-[#D4AF37]/40 text-xs font-bold text-[#E6C280] hover:border-[#D4AF37] transition-all shadow-md"
              >
                <Languages className="w-4 h-4 text-[#14B8A6]" />
                <span>{uiLanguage === 'en' ? 'தமிழ்' : 'English'}</span>
              </button>

              <button
                onClick={() => scrollToSection('digitize')}
                className="hidden sm:flex items-center space-x-2 px-4 py-2 text-xs font-bold bg-gradient-to-r from-[#D4AF37] to-[#B89228] text-[#0D0B08] rounded-xl hover:brightness-110 transition-all shadow-lg"
              >
                <Sparkles className="w-4 h-4 text-[#0D0B08]" />
                <span>{t.ctaStartDigitizing}</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* MAIN BODY */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-16">

        {/* HERO SECTION */}
        <section id="home" className="relative pt-6 pb-10 rounded-3xl heritage-card-glow overflow-hidden p-8 sm:p-12 text-center border border-[#D4AF37]/35">
          <div className="relative z-10 max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-[#1A140F] border border-[#D4AF37]/40 shadow-inner">
              <span className="w-2 h-2 rounded-full bg-[#14B8A6] animate-pulse"></span>
              <span className="text-xs font-serif-heading font-bold text-[#E6C280] uppercase tracking-widest">
                மருதுளிர் · Palm-Leaf & Stone Inscription Restoration Platform
              </span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-extrabold font-serif-heading gold-gradient-text leading-tight tracking-wide">
              {t.heroTitle}
            </h1>

            <p className="text-base sm:text-lg text-[#A09382] font-normal leading-relaxed">
              {t.heroSubtitle}
            </p>

            <div className="pt-2 flex justify-center">
              <button
                onClick={() => scrollToSection('digitize')}
                className="inline-flex items-center space-x-3 px-8 py-3.5 text-sm font-bold bg-gradient-to-r from-[#D4AF37] via-[#E6C280] to-[#D4AF37] text-[#0D0B08] rounded-2xl hover:brightness-110 transition-all shadow-xl hover:shadow-gold-glow transform hover:-translate-y-0.5"
              >
                <Sparkles className="w-5 h-5 text-[#0D0B08]" />
                <span className="tracking-wide uppercase font-extrabold">{t.ctaStartDigitizing}</span>
                <ArrowRight className="w-4 h-4 text-[#0D0B08]" />
              </button>
            </div>
          </div>
        </section>

        {/* DIGITIZE & RESTORE SECTION */}
        <section id="digitize" className="space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold font-serif-heading gold-gradient-text">
              {t.uploadTitle}
            </h2>
            <p className="text-sm text-[#A09382]">
              Select source type and upload manuscript or stone inscription image to run OCR and scholar review workflow
            </p>
          </div>

          {/* DUAL SOURCE TYPE SELECTION CARD */}
          <div className="max-w-2xl mx-auto space-y-3">
            <label className="block text-xs font-bold text-[#E6C280] uppercase tracking-widest text-center">
              {t.selectSourceType}
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              {/* Option 1: Palm Leaf Manuscript */}
              <div 
                onClick={() => setSourceType('palm-leaf')}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start space-x-3.5 ${
                  sourceType === 'palm-leaf'
                    ? 'bg-gradient-to-br from-[#1E1711] to-[#140F0B] border-[#D4AF37] shadow-xl'
                    : 'bg-[#120E0A] border-[#3A2E22] opacity-70 hover:opacity-100 hover:border-[#D4AF37]/50'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  sourceType === 'palm-leaf' ? 'bg-[#D4AF37]/20 text-[#E6C280] border border-[#D4AF37]' : 'bg-[#1A140F] text-[#A09382]'
                }`}>
                  <BookOpen className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-sm text-[#FFF5E4]">
                      {t.sourcePalmLeaf}
                    </h3>
                  </div>
                  <p className="text-[11px] text-[#A09382] leading-tight mt-1">
                    {t.sourcePalmLeafDesc}
                  </p>
                </div>
              </div>

              {/* Option 2: Stone Inscription */}
              <div 
                onClick={() => setSourceType('stone-inscription')}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start space-x-3.5 ${
                  sourceType === 'stone-inscription' || sourceType === 'inscription'
                    ? 'bg-gradient-to-br from-[#1E1711] to-[#140F0B] border-[#14B8A6] shadow-xl'
                    : 'bg-[#120E0A] border-[#3A2E22] opacity-70 hover:opacity-100 hover:border-[#14B8A6]/50'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  sourceType === 'stone-inscription' || sourceType === 'inscription' ? 'bg-[#14B8A6]/20 text-[#2DD4BF] border border-[#14B8A6]' : 'bg-[#1A140F] text-[#A09382]'
                }`}>
                  <Scroll className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-sm text-[#FFF5E4]">
                      {t.sourceStoneInscription}
                    </h3>
                  </div>
                  <p className="text-[11px] text-[#A09382] leading-tight mt-1">
                    {t.sourceStoneInscriptionDesc}
                  </p>
                </div>
              </div>

            </div>
          </div>

          {/* UPLOAD FORM */}
          <div className="max-w-3xl mx-auto heritage-card rounded-3xl p-6 sm:p-8 space-y-6">
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A09382] uppercase tracking-wider">
                {t.inputTitleLabel}
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={t.inputTitlePlaceholder}
                className="w-full px-4 py-3 rounded-xl bg-[#120E0A] border border-[#D4AF37]/30 text-[#E8DCC4] placeholder-[#665B4E] focus:outline-none focus:border-[#D4AF37] text-sm transition-all"
              />
            </div>

            {!imagePreview ? (
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-[#D4AF37]/40 hover:border-[#D4AF37] rounded-2xl p-8 text-center bg-[#120E0A]/60 hover:bg-[#1A140F]/80 transition-all cursor-pointer space-y-4 group"
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/png, image/jpeg, image/jpg, image/webp"
                  className="hidden"
                />
                <div className="w-16 h-16 rounded-full bg-[#1A140F] border border-[#D4AF37]/30 flex items-center justify-center mx-auto text-[#E6C280] group-hover:scale-110 transition-all shadow-md">
                  <Upload className="w-8 h-8" />
                </div>
                <div className="space-y-1">
                  <p className="text-base font-bold text-[#FFF5E4]">
                    {t.uploadDragText}
                  </p>
                  <p className="text-xs text-[#14B8A6] font-semibold">
                    {t.uploadChooseText}
                  </p>
                </div>
                <p className="text-[11px] text-[#A09382]">
                  {t.uploadFormats}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative rounded-2xl overflow-hidden border border-[#D4AF37]/40 bg-[#120E0A] max-h-80 flex items-center justify-center p-3">
                  <img
                    src={imagePreview}
                    alt="Artifact Preview"
                    className="max-h-72 w-auto object-contain rounded-lg shadow-lg"
                  />
                  <button
                    onClick={() => { setSelectedFile(null); setImagePreview(null); }}
                    className="absolute top-4 right-4 p-2 rounded-full bg-[#0D0B08]/80 text-[#E8DCC4] hover:text-red-400 hover:bg-black transition-all border border-white/20"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex items-center justify-between px-2 text-xs text-[#A09382]">
                  <span className="font-semibold text-[#E8DCC4] truncate max-w-md">
                    📄 {selectedFile.name}
                  </span>
                  <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${stDisplay.badgeBg}`}>
                    {stDisplay.label}
                  </span>
                </div>
              </div>
            )}

            {uploadError && (
              <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/50 flex items-center space-x-3 text-red-300 text-sm">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <span>{uploadError}</span>
              </div>
            )}

            <div>
              <button
                onClick={handleRunPipeline}
                disabled={!selectedFile || isUploading || isRunningOCR}
                className={`w-full py-4 rounded-2xl font-bold text-sm uppercase tracking-wider flex items-center justify-center space-x-3 transition-all shadow-xl ${
                  !selectedFile || isUploading || isRunningOCR
                    ? 'bg-[#1A140F] text-[#665B4E] border border-[#3A2E22] cursor-not-allowed'
                    : 'bg-gradient-to-r from-[#D4AF37] via-[#E6C280] to-[#D4AF37] text-[#0D0B08] hover:brightness-110 shadow-gold-glow'
                }`}
              >
                {isUploading || isIdentifying || isRunningOCR || isRestoring ? (
                  <>
                    <RefreshCw className="w-5 h-5 text-[#0D0B08] animate-spin" />
                    <span>Processing Analysis & Candidate Restoration...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 text-[#0D0B08]" />
                    <span>{t.btnRunPipeline}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {/* SCHOLAR REVIEW STAGE (BEFORE FINAL OUTPUT) */}
        {restorationData && !isScholarApproved && (
          <section id="scholar-review-section" className="heritage-card rounded-3xl p-6 sm:p-8 space-y-6 border-2 border-[#D4AF37]">
            <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-4">
              <div>
                <div className="flex items-center space-x-3">
                  <ShieldCheck className="w-6 h-6 text-[#D4AF37]" />
                  <h3 className="text-xl font-bold font-serif-heading gold-gradient-text">
                    {t.scholarReviewTitle}
                  </h3>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold border flex items-center space-x-1.5 ${stDisplay.badgeBg}`}>
                    {stDisplay.icon}
                    <span>Source Type: {stDisplay.label}</span>
                  </span>
                </div>
                <p className="text-xs text-[#A09382] mt-1">
                  {t.scholarReviewSubtitle}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Left Column: Image + Raw OCR */}
              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#3A2E22] space-y-2">
                  <span className="text-xs font-bold text-[#A09382] uppercase tracking-wider">Original Uploaded Image</span>
                  {imagePreview && (
                    <img src={imagePreview} alt="Manuscript" className="max-h-48 w-auto mx-auto object-contain rounded-lg border border-[#3A2E22]" />
                  )}
                </div>

                <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#3A2E22] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#A09382] uppercase tracking-wider">Raw Sarvam OCR Output</span>
                    <span className="text-[10px] text-[#D4AF37]">Confidence: {(ocrData?.confidence || 0.95) * 100}%</span>
                  </div>
                  <p className="font-tamil-serif text-sm text-[#FFF5E4] whitespace-pre-wrap bg-[#14100C] p-3 rounded-xl border border-[#D4AF37]/20">
                    {ocrData?.extracted_text}
                  </p>
                </div>

                {/* Restoration Output Display Section */}
                <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#D4AF37]/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#E6C280] uppercase tracking-wider flex items-center space-x-1.5">
                      <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                      <span>Restored Tamil Text (Lexicon Grounded)</span>
                    </span>
                    <span className="text-[10px] text-[#14B8A6] font-semibold">
                      Restoration Confidence: {((restorationData?.confidence || 0.85) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <p className="font-tamil-serif text-sm text-[#FFF5E4] whitespace-pre-wrap bg-[#14100C] p-3 rounded-xl border border-[#D4AF37]/30">
                    {restorationData?.restored_text || ocrData?.extracted_text || "Restored Tamil text is unavailable."}
                  </p>
                </div>
              </div>

              {/* Right Column: Source-Specific Damage Evidence & Candidates */}
              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#D4AF37]/40 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#E6C280] uppercase tracking-wider flex items-center space-x-2">
                      <Search className="w-4 h-4 text-[#14B8A6]" />
                      <span>RESTORATION EVIDENCE</span>
                    </span>
                    <span className="text-[10px] text-[#A09382]">Original OCR → Restored Word → Classical Score</span>
                  </div>

                  {(() => {
                    const actualCorrections = (restorationData?.corrections || []).filter(
                      (c) => c.original && c.corrected && c.original !== c.corrected
                    );

                    if (actualCorrections.length === 0) {
                      return (
                        <div className="p-3.5 rounded-xl bg-[#14100C] border border-[#3A2E22] text-center">
                          <p className="text-xs text-[#A09382] font-semibold">No lexical corrections detected.</p>
                        </div>
                      );
                    }

                    return (
                      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                        <div className="grid grid-cols-3 gap-2 px-3 py-1.5 text-[11px] font-bold text-[#A09382] border-b border-[#3A2E22]">
                          <span>Original OCR</span>
                          <span>Restored Word</span>
                          <span className="text-right">Classical Score</span>
                        </div>
                        {actualCorrections.map((corr, idx) => {
                          const scoreDisplay = corr.score_percent || `${Math.round((corr.confidence || 0.85) * 100)}%`;
                          return (
                            <div key={idx} className="grid grid-cols-3 gap-2 p-2.5 rounded-xl bg-[#14100C] border border-[#D4AF37]/30 text-xs items-center">
                              <span className="font-tamil-serif text-red-300/90 font-medium truncate">{corr.original}</span>
                              <span className="font-tamil-serif text-[#2DD4BF] font-semibold truncate">{corr.corrected}</span>
                              <span className="text-right font-bold text-[#E6C280]">{scoreDisplay}</span>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}
                </div>

                {/* Editable Textarea for Scholar Approval */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-[#E6C280] uppercase tracking-wider flex items-center space-x-1.5">
                    <Edit3 className="w-4 h-4 text-[#D4AF37]" />
                    <span>{t.approvedClassicalLabel}</span>
                  </label>
                  <textarea
                    rows={4}
                    value={editableClassicalTamil}
                    onChange={(e) => setEditableClassicalTamil(e.target.value)}
                    className="w-full p-4 rounded-2xl bg-[#14100C] border-2 border-[#D4AF37] font-tamil-serif text-base text-[#FFF5E4] focus:outline-none focus:ring-2 focus:ring-[#D4AF37] transition-all shadow-inner"
                    placeholder="Review and edit the Classical Tamil text if required..."
                  />
                </div>

                <button
                  onClick={handleApproveScholarReview}
                  disabled={isConvertingModern || isTranslating}
                  className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#D4AF37] via-[#E6C280] to-[#D4AF37] text-[#0D0B08] font-extrabold text-sm uppercase tracking-wider flex items-center justify-center space-x-3 hover:brightness-110 shadow-xl transition-all"
                >
                  {isConvertingModern || isTranslating ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin text-[#0D0B08]" />
                      <span>Generating Student Modern Tamil & Translation...</span>
                    </>
                  ) : (
                    <>
                      <CheckSquare className="w-5 h-5 text-[#0D0B08]" />
                      <span>{t.btnApproveAndContinue}</span>
                    </>
                  )}
                </button>
              </div>

            </div>
          </section>
        )}
        {isScholarApproved && (
          <section id="final-results-section" className="space-y-8">
            
            {/* Header Status Badge */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-[#1E1711] to-[#140F0B] border border-[#D4AF37]/40 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-400" />
                <div>
                  <h3 className="font-bold text-base text-[#FFF5E4] font-serif-heading">
                    Restoration & Modernization Complete
                  </h3>
                  <p className="text-xs text-[#A09382]">
                    Scholar Approved & Verified Archives Record
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center space-x-1.5 ${stDisplay.badgeBg}`}>
                  {stDisplay.icon}
                  <span>Source Type: {stDisplay.label}</span>
                </span>

                <button
                  onClick={handleReset}
                  className="px-4 py-2 rounded-xl bg-[#1A140F] border border-[#D4AF37]/40 text-xs font-bold text-[#E6C280] hover:border-[#D4AF37]"
                >
                  Process Another Image
                </button>
              </div>
            </div>

            {/* 3 CLEAN RESULT CARDS */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

              {/* CARD 1: Scholar-Approved Classical Tamil */}
              <div className="heritage-card rounded-3xl p-6 space-y-4 border-2 border-[#D4AF37]/50 flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-center justify-between border-b border-[#D4AF37]/20 pb-3">
                    <h3 className="font-bold text-base font-serif-heading text-[#FFF5E4]">
                      {t.card1Title}
                    </h3>
                    <button
                      onClick={() => handleCopy(editableClassicalTamil, 'card1')}
                      className="p-1.5 rounded-lg bg-[#14100C] border border-[#D4AF37]/30 text-xs text-[#E6C280]"
                    >
                      {copiedCard === 'card1' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-[#D4AF37]" />}
                    </button>
                  </div>

                  <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#3A2E22] min-h-[180px]">
                    <p className="font-tamil-serif text-base text-[#FFF5E4] leading-relaxed whitespace-pre-wrap">
                      {editableClassicalTamil}
                    </p>
                  </div>
                </div>
                <div className="text-[11px] text-[#A09382] font-semibold text-center pt-2">
                  ✓ Verified by Scholar Review
                </div>
              </div>

              {/* CARD 2: Modern Readable Tamil (Student Paragraph) */}
              <div className="heritage-card rounded-3xl p-6 space-y-4 border-2 border-[#14B8A6]/60 flex flex-col justify-between shadow-teal-glow">
                <div className="space-y-3">
                  <div className="flex items-center justify-between border-b border-[#14B8A6]/20 pb-3">
                    <div>
                      <h3 className="font-bold text-base font-serif-heading text-[#FFF5E4]">
                        {t.card2Title}
                      </h3>
                    </div>
                    <button
                      onClick={() => handleCopy(modernTamilData?.modern_tamil_text, 'card2')}
                      className="p-1.5 rounded-lg bg-[#14100C] border border-[#14B8A6]/30 text-xs text-[#2DD4BF]"
                    >
                      {copiedCard === 'card2' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-[#14B8A6]" />}
                    </button>
                  </div>

                  <p className="text-[11px] text-[#2DD4BF] font-tamil-sans">
                    {t.card2Subtitle}
                  </p>

                  <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#3A2E22] min-h-[180px]">
                    <p className="font-tamil-sans text-base text-[#FFF5E4] font-medium leading-relaxed">
                      {modernTamilData?.modern_tamil_text}
                    </p>
                  </div>
                </div>
                <div className="text-[11px] text-[#2DD4BF] font-semibold text-center pt-2">
                  ✓ Contemporary Student Paragraph
                </div>
              </div>

              {/* CARD 3: English Translation */}
              <div className="heritage-card rounded-3xl p-6 space-y-4 border-2 border-[#D4AF37]/50 flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-center justify-between border-b border-[#D4AF37]/20 pb-3">
                    <div>
                      <h3 className="font-bold text-base font-serif-heading text-[#FFF5E4]">
                        {t.card3Title}
                      </h3>
                    </div>
                    <button
                      onClick={() => handleCopy(translationData?.english_translation, 'card3')}
                      className="p-1.5 rounded-lg bg-[#14100C] border border-[#D4AF37]/30 text-xs text-[#E6C280]"
                    >
                      {copiedCard === 'card3' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-[#D4AF37]" />}
                    </button>
                  </div>

                  <p className="text-[11px] text-[#A09382]">
                    {t.card3Subtitle}
                  </p>

                  <div className="p-4 rounded-2xl bg-[#0D0B08] border border-[#3A2E22] min-h-[180px]">
                    <p className="font-sans text-base text-[#FFF5E4] leading-relaxed">
                      {translationData?.english_translation}
                    </p>
                  </div>
                </div>
                <div className="text-[11px] text-[#A09382] font-semibold text-center pt-2">
                  ✓ Natural English Translation
                </div>
              </div>

            </div>
          </section>
        )}

      </main>

      {/* FOOTER */}
      <footer className="bg-[#090705] border-t border-[#D4AF37]/20 py-8 text-center text-xs text-[#665B4E] space-y-2">
        <p className="font-bold text-[#E6C280] font-serif-heading text-sm">
          மருதுளிர் · MARUTHULIR
        </p>
        <p>{t.subtitle}</p>
        <p className="text-[10px] text-[#4A4035]">
          Powered by Sarvam AI Vision OCR, Classical Tamil Reference Lexicon & Student Modernization LLM Engine.
        </p>
      </footer>

    </div>
  );
}
