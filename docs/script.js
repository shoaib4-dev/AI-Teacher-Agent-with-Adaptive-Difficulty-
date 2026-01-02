// ============================================
// Global State Management
// ============================================

const appState = {
    currentSection: 'home',
    currentUser: null,
    authToken: null,
    isAuthenticated: false,
    studentPerformance: {
        totalQuizzes: 0,
        correctAnswers: 0,
        averageScore: 0.0,
        difficultyLevel: 'Beginner',
        topicsCovered: [],
        performanceHistory: []
    },
    currentQuiz: null,
    quizAnswers: {},
    conversationHistory: [],
    studyPath: [],
    uploadedFiles: [],
    isVoiceRecording: false,
    recognition: null,
    questionPool: [],
    selectedQuestions: [],
    currentTopicExplanation: null,
    uploadedPDF: null
};

// Topic explanations data (placeholder - will be replaced with backend API)
const topicExplanations = {
    1: {
        title: "Python Basics",
        content: "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python's syntax allows programmers to express concepts in fewer lines of code than would be possible in languages such as C++ or Java.",
        keyConcepts: ["Variables", "Data Types", "Control Flow", "Functions", "Classes", "Modules"]
    },
    2: {
        title: "Machine Learning",
        content: "Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms to analyze data, identify patterns, and make predictions or decisions. ML algorithms build mathematical models based on training data to make predictions or decisions.",
        keyConcepts: ["Supervised Learning", "Unsupervised Learning", "Neural Networks", "Training", "Validation", "Overfitting"]
    },
    3: {
        title: "Data Structures",
        content: "Data structures are ways of organizing and storing data in a computer so that it can be accessed and modified efficiently. Different data structures are suited to different kinds of applications, and some are highly specialized to specific tasks.",
        keyConcepts: ["Arrays", "Linked Lists", "Stacks", "Queues", "Trees", "Graphs", "Hash Tables"]
    },
    4: {
        title: "Algorithms",
        content: "An algorithm is a step-by-step procedure for solving a problem or accomplishing a task. Algorithms are fundamental to computer science and are used to process data, perform calculations, and automate reasoning.",
        keyConcepts: ["Sorting", "Searching", "Dynamic Programming", "Greedy Algorithms", "Graph Algorithms", "Complexity Analysis"]
    },
    5: {
        title: "Neural Networks",
        content: "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information. Deep neural networks with multiple layers can learn complex patterns in data.",
        keyConcepts: ["Perceptrons", "Backpropagation", "Activation Functions", "Convolutional Networks", "Recurrent Networks", "Deep Learning"]
    },
    6: {
        title: "Natural Language Processing",
        content: "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language. NLP combines computational linguistics with machine learning and deep learning models.",
        keyConcepts: ["Tokenization", "Sentiment Analysis", "Named Entity Recognition", "Language Models", "Text Classification", "Machine Translation"]
    }
};

// ============================================
// Navigation Functions
// ============================================

function initNavigation() {
    // Handle navigation clicks
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('href').substring(1);
            showSection(sectionId);
        });
    });

    // Handle hamburger menu
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.navbar')) {
            navMenu.classList.remove('active');
        }
    });

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

function showSection(sectionId) {
    // Special handling for YouTube RAG section - redirect to external Streamlit app
    if (sectionId === 'youtube-rag') {
        window.open('https://youtube-video-query-solver-o3d2na4s4lyhkbrj5cr9hu.streamlit.app/', '_blank');
        return;
    }
    
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        appState.currentSection = sectionId;
    }

    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
        }
    });

    // Close mobile menu
    document.getElementById('navMenu').classList.remove('active');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Load section-specific data
    loadSectionData(sectionId);
}

function loadSectionData(sectionId) {
    switch(sectionId) {
        case 'performance':
            // Ensure canvas is properly sized before updating
            setTimeout(() => {
                const canvas = document.getElementById('performanceChart');
                if (canvas) {
                    const container = canvas.parentElement;
                    if (container && container.offsetWidth > 0) {
                        canvas.width = container.offsetWidth;
                        canvas.height = 300;
                    }
                }
            updatePerformanceDashboard();
            }, 100);
            break;
        case 'chat':
            // Chat is already initialized
            break;
    }
}

// ============================================
// Topic Functions
// ============================================

function toggleTopicMode() {
    const customInput = document.getElementById('customTopicInput');
    const predefinedSelect = document.getElementById('predefinedTopicSelect');
    const mode = document.querySelector('input[name="topicMode"]:checked').value;

    if (mode === 'custom') {
        customInput.classList.remove('hidden');
        predefinedSelect.classList.add('hidden');
    } else {
        customInput.classList.add('hidden');
        predefinedSelect.classList.remove('hidden');
    }
}

async function loadTopic() {
    // Check authentication
    if (!requireAuth('load topic explanations')) {
        return;
    }
    
    const mode = document.querySelector('input[name="topicMode"]:checked').value;
    let topicName = '';
    let explanation = null;

    // Show loading state
    const loadBtn = document.querySelector('.action-button');
    const originalText = loadBtn.innerHTML;
    loadBtn.disabled = true;
    loadBtn.innerHTML = '<span>Loading...</span>';

    try {
        if (mode === 'custom') {
            const customInput = document.getElementById('customTopic');
            topicName = customInput.value.trim();
            
            if (!topicName) {
                alert('Please enter a topic');
                return;
            }

            // Call backend API for custom topics
            const response = await fetch('http://localhost:5000/api/topics/explain', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic_name: topicName
                })
            });

            if (!response.ok) {
                throw new Error(`Backend error: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Use backend response
            explanation = {
                title: data.topic,
                content: data.explanation,
                youtubeLinks: data.youtube_links || [],
                websiteReferences: data.website_references || []
            };
            
        } else {
            const topicSelect = document.getElementById('topicSelect');
            const topicId = parseInt(topicSelect.value);

            if (!topicId) {
                alert('Please select a topic');
                return;
            }

            // For predefined topics, also call backend API
            const predefinedTopic = topicExplanations[topicId];
            topicName = predefinedTopic ? predefinedTopic.title : '';
            
            if (!topicName) {
                alert('Topic explanation not found');
                return;
            }

            // Call backend API for predefined topics too
            const response = await fetch('http://localhost:5000/api/topics/explain', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic_name: topicName
                })
            });

            if (!response.ok) {
                throw new Error(`Backend error: ${response.statusText}`);
            }

            const data = await response.json();
            
            explanation = {
                title: data.topic,
                content: data.explanation,
                youtubeLinks: data.youtube_links || [],
                websiteReferences: data.website_references || []
            };
        }

        // Store explanation for reference
        appState.currentTopicExplanation = explanation;

        // Display topic content
        const topicContent = document.getElementById('topicContent');
        const topicTitle = document.getElementById('topicTitle');
        const topicExplanation = document.getElementById('topicExplanation');
        const topicConcepts = document.getElementById('topicConcepts');
        const topicResources = document.getElementById('topicResources');

        topicTitle.textContent = explanation.title;
        // Display explanation as formatted paragraphs
        let formattedExplanation = explanation.content || '';
        
        console.log('Explanation received:', formattedExplanation.substring(0, 200));
        console.log('Has double newlines:', formattedExplanation.includes('\n\n'));
        console.log('Has single newlines:', formattedExplanation.includes('\n'));
        
        // Normalize newlines - handle both \n\n and \r\n\r\n
        formattedExplanation = formattedExplanation.replace(/\r\n/g, '\n');
        
        // Split by double newlines first (paragraph breaks)
        let paragraphs = formattedExplanation.split(/\n\s*\n/);
        
        // If no double newlines found, try splitting by single newlines
        if (paragraphs.length === 1 && formattedExplanation.includes('\n')) {
            paragraphs = formattedExplanation.split(/\n/);
        }
        
        // If still no paragraphs, try to create them from sentences
        if (paragraphs.length === 1 || (paragraphs.length === 1 && paragraphs[0].trim().length > 500)) {
            // Split into sentences and group into paragraphs
            const sentences = formattedExplanation.split(/[.!?]+/).filter(s => s.trim().length > 10);
            const sentencesPerParagraph = Math.max(3, Math.ceil(sentences.length / 4));
            paragraphs = [];
            
            for (let i = 0; i < sentences.length; i += sentencesPerParagraph) {
                const paragraphSentences = sentences.slice(i, i + sentencesPerParagraph);
                const paraText = paragraphSentences.join('. ').trim();
                if (paraText.length > 0) {
                    paragraphs.push(paraText + (paraText.endsWith('.') ? '' : '.'));
                }
            }
        }
        
        // Format as HTML paragraphs
        const htmlParagraphs = paragraphs
            .map(p => p.trim())
            .filter(p => p.length > 0)
            .map(p => `<p>${p}</p>`)
            .join('');
        
        console.log('Number of paragraphs created:', paragraphs.length);
        topicExplanation.innerHTML = htmlParagraphs || `<p>${explanation.content}</p>`;

        // Hide concept buttons section (no longer needed)
        if (topicConcepts) {
            topicConcepts.innerHTML = '';
            topicConcepts.style.display = 'none';
        }

        // Display resources from backend
        displayTopicResources(explanation);

        topicContent.classList.remove('hidden');
        topicResources.classList.remove('hidden');

        // Add to conversation history
        addToHistory('topic_loaded', `Loaded topic: ${topicName}`);

        // Animate content appearance
        topicContent.style.animation = 'fadeIn 0.5s ease';
        
    } catch (error) {
        console.error('Error loading topic:', error);
        alert(`Failed to load topic: ${error.message}\n\nMake sure the backend is running on http://localhost:5000`);
    } finally {
        loadBtn.disabled = false;
        loadBtn.innerHTML = originalText;
    }
}

async function showConceptDescription(concept, fullExplanation, index) {
    // Create or update concept description display
    let conceptDescDiv = document.getElementById('conceptDescription');
    
    if (!conceptDescDiv) {
        conceptDescDiv = document.createElement('div');
        conceptDescDiv.id = 'conceptDescription';
        conceptDescDiv.className = 'concept-description';
        
        // Insert after topicExplanation
        const topicExplanation = document.getElementById('topicExplanation');
        topicExplanation.parentNode.insertBefore(conceptDescDiv, topicExplanation.nextSibling);
    }
    
    // Show loading state
    conceptDescDiv.innerHTML = `
        <div class="concept-desc-header">
            <h4>${concept}</h4>
            <button class="close-concept-btn" onclick="closeConceptDescription()">×</button>
        </div>
        <div class="concept-desc-content">
            <p>Loading description...</p>
        </div>
    `;
    conceptDescDiv.classList.remove('hidden');
    
    // Generate description based on concept type
    let description = '';
    // Try multiple sources for topic name
    let topicName = appState.currentTopicExplanation?.title || 
                   appState.currentTopicExplanation?.topic || 
                   document.getElementById('topicTitle')?.textContent || 
                   '';
    
    // If still no topic name, try to get from custom input
    if (!topicName) {
        const customTopicInput = document.getElementById('customTopicInput');
        if (customTopicInput && customTopicInput.value) {
            topicName = customTopicInput.value.trim();
        }
    }
    
    // Get real AI-generated description from backend topics API
    try {
        const queryTopic = `${topicName} - ${concept}`;
        console.log(`Fetching concept description for: ${queryTopic}`);
        
        const response = await fetch('http://localhost:5000/api/topics/explain', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic_name: queryTopic
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            description = data.explanation || '';
            
            console.log(`Received explanation for ${concept}:`, description.substring(0, 100) + '...');
            
            // Always use backend response if it exists and has content
            if (description && description.trim().length > 50) {
                // Use the AI-generated explanation from backend - it's concept-specific!
                // The backend now generates different content for each concept type
            } else {
                console.warn(`Backend returned empty/short explanation for ${concept}, using fallback`);
                // Only fallback if backend returns empty or very short response
                description = generateConceptDescription(concept, topicName, fullExplanation);
            }
        } else {
            console.error(`Backend error for ${concept}:`, response.status, response.statusText);
            // Generate from full explanation only if API call fails
            description = generateConceptDescription(concept, topicName, fullExplanation);
        }
    } catch (error) {
        console.error('Error getting concept description:', error);
        // Generate from full explanation only if network error
        description = generateConceptDescription(concept, topicName, fullExplanation);
    }
    
    conceptDescDiv.innerHTML = `
        <div class="concept-desc-header">
            <h4>${concept}</h4>
            <button class="close-concept-btn" onclick="closeConceptDescription()">×</button>
        </div>
        <div class="concept-desc-content">
            ${description.split('\n').map(p => p.trim() ? `<p>${p}</p>` : '').join('')}
        </div>
    `;
    
    // Highlight the clicked button
    document.querySelectorAll('.concept-button').forEach(btn => {
        btn.classList.remove('active');
    });
    const clickedBtn = document.querySelector(`[data-concept="${concept}"]`);
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }
}

function generateConceptDescription(concept, topicName, fullExplanation) {
    // Split explanation into meaningful sentences
    const sentences = fullExplanation.split(/[.!?]+/).filter(s => s.trim().length > 20);
    const totalSentences = sentences.length;
    
    switch(concept.toLowerCase()) {
        case 'introduction':
            // Use first 2-3 sentences for introduction
            const introSentences = sentences.slice(0, Math.min(3, totalSentences));
            const introText = introSentences.join('. ').trim();
            return `Introduction to ${topicName}:\n\n${introText}.\n\nThis topic provides fundamental knowledge and serves as a starting point for deeper understanding. It covers the basics and essential concepts that form the foundation of ${topicName}. Understanding the introduction is crucial before diving into more complex aspects.`;
            
        case 'core concepts':
            // Use middle sentences for core concepts
            const startIdx = Math.floor(totalSentences / 4);
            const endIdx = Math.min(startIdx + 4, totalSentences);
            const coreSentences = sentences.slice(startIdx, endIdx);
            const coreText = coreSentences.join('. ').trim();
            return `Core Concepts of ${topicName}:\n\nThe essential principles and fundamental ideas that form the foundation of ${topicName}. ${coreText}.\n\nThese concepts are crucial for understanding the topic and building advanced knowledge. They represent the key building blocks that every learner should master. Without understanding these core concepts, it's difficult to progress to more advanced topics.`;
            
        case 'applications':
            // Use sentences that mention applications, or last few sentences
            const appSentences = sentences.filter(s => 
                s.toLowerCase().includes('application') || 
                s.toLowerCase().includes('use') || 
                s.toLowerCase().includes('example') ||
                s.toLowerCase().includes('practice')
            );
            const finalAppSentences = appSentences.length > 0 
                ? appSentences.slice(0, 3) 
                : sentences.slice(Math.max(0, totalSentences - 3), totalSentences);
            const appText = finalAppSentences.join('. ').trim();
            return `Applications of ${topicName}:\n\n${topicName} has numerous practical applications in real-world scenarios. ${appText}.\n\nIt is used across various industries and fields to solve problems and create innovative solutions. Understanding these applications helps see the practical value and relevance of ${topicName} in everyday life and professional contexts.`;
            
        case 'advanced topics':
            return `Advanced Topics in ${topicName}:\n\nFor those who have mastered the basics, advanced topics explore complex aspects, advanced techniques, and cutting-edge developments in ${topicName}. These topics require a solid foundation and deeper understanding of the subject matter.\n\nAdvanced study of ${topicName} involves exploring specialized areas, complex problem-solving techniques, and staying updated with the latest research and developments in the field. This level of study is typically pursued by professionals, researchers, and those seeking expertise in ${topicName}.`;
            
        default:
            // For other concepts, use a mix
            const defaultSentences = sentences.slice(0, Math.min(3, totalSentences));
            const defaultText = defaultSentences.join('. ').trim();
            return `${concept} in ${topicName}:\n\n${defaultText}.\n\nThis is an important aspect of ${topicName} that covers key principles and practical applications related to ${concept}. Understanding this concept is essential for a comprehensive grasp of ${topicName} and its various dimensions.`;
    }
}

function closeConceptDescription() {
    const conceptDescDiv = document.getElementById('conceptDescription');
    if (conceptDescDiv) {
        conceptDescDiv.classList.add('hidden');
    }
    
    // Remove active state from buttons
    document.querySelectorAll('.concept-button').forEach(btn => {
        btn.classList.remove('active');
    });
}

function displayTopicResources(explanation) {
    // Use resources from backend API response
    const youtubeLinks = document.getElementById('youtubeLinks');
    const websiteReferences = document.getElementById('websiteReferences');
    const topicName = explanation.title || '';

    // Clear previous resources
    youtubeLinks.innerHTML = '';
    websiteReferences.innerHTML = '';

    // YouTube Video Link from backend (single video only)
    let youtubeUrl;
    let youtubeTitle;
    
    if (explanation.youtubeLinks && explanation.youtubeLinks.length > 0) {
        // Use the first (and only) YouTube link from backend
        youtubeUrl = explanation.youtubeLinks[0].url;
        youtubeTitle = explanation.youtubeLinks[0].title || `${topicName} - Video Tutorial`;
    } else {
        // Fallback: Generate YouTube video search link
        const searchQuery = `${topicName} tutorial`.replace(/\s+/g, '+');
        youtubeUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(searchQuery)}&sp=EgIQAQ%3D%3D`;
        youtubeTitle = `${topicName} - Video Tutorial`;
    }
    
    // Create and display single YouTube video link
    const youtubeElement = document.createElement('a');
    youtubeElement.href = youtubeUrl;
    youtubeElement.target = '_blank';
    youtubeElement.rel = 'noopener noreferrer';
    youtubeElement.className = 'resource-link';
    youtubeElement.innerHTML = `<span class="resource-link-icon">🎥</span><span>${youtubeTitle}</span>`;
    youtubeElement.style.cursor = 'pointer';
    youtubeElement.style.textDecoration = 'none';
    
    youtubeLinks.appendChild(youtubeElement);
    
    console.log('[DEBUG] YouTube video link created:', youtubeUrl);

    // Website References from backend (Wikipedia only - single link)
    // ALWAYS generate Wikipedia URL from topic name to ensure it's correct
    const wikiTopic = topicName.trim().replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_-]/g, '');
    let wikiUrl = `https://en.wikipedia.org/wiki/${wikiTopic}`;
    
    // Check backend response, but only use it if it's a valid Wikipedia URL
    if (explanation.websiteReferences && explanation.websiteReferences.length > 0 && explanation.websiteReferences[0].url) {
        const backendUrl = explanation.websiteReferences[0].url;
        console.log('[DEBUG] Backend returned URL:', backendUrl);
        
        // Only use backend URL if it's a valid Wikipedia URL (not Google or search)
        if (backendUrl.includes('wikipedia.org/wiki') && 
            !backendUrl.includes('google.com') && 
            !backendUrl.includes('search')) {
            wikiUrl = backendUrl;
            console.log('[DEBUG] Using valid backend Wikipedia URL:', wikiUrl);
        } else {
            console.warn('[WARNING] Backend returned invalid URL (Google/search), using generated Wikipedia URL instead');
            console.log('[DEBUG] Generated Wikipedia URL:', wikiUrl);
        }
    } else {
        console.log('[DEBUG] No backend URL, generated Wikipedia URL:', wikiUrl);
    }
    
    // Final validation: Ensure it's a direct Wikipedia page link
    if (!wikiUrl.startsWith('https://en.wikipedia.org/wiki/')) {
        console.error('[ERROR] Invalid Wikipedia URL format, regenerating:', wikiUrl);
        wikiUrl = `https://en.wikipedia.org/wiki/${wikiTopic}`;
    }
    
    console.log('[DEBUG] Final Wikipedia URL to use:', wikiUrl);
    
    // Create and display the Wikipedia link
    const siteElement = document.createElement('a');
    siteElement.href = wikiUrl;
    siteElement.target = '_blank';
    siteElement.rel = 'noopener noreferrer'; // Security best practice
    siteElement.className = 'resource-link';
    siteElement.innerHTML = `<span class="resource-link-icon">🌐</span><span>${topicName} - Wikipedia</span>`;
    
    // Ensure the link is clickable
    siteElement.style.cursor = 'pointer';
    siteElement.style.textDecoration = 'none';
    
    // Add click event as backup (in case default behavior is prevented)
    siteElement.addEventListener('click', function(e) {
        console.log('[DEBUG] Wikipedia link clicked, URL:', wikiUrl);
        // If default was prevented, manually open
        if (e.defaultPrevented) {
            e.preventDefault();
            window.open(wikiUrl, '_blank', 'noopener,noreferrer');
        }
    });
    
    websiteReferences.appendChild(siteElement);
    
    console.log('[DEBUG] Final Wikipedia link created - href:', siteElement.href);
    console.log('[DEBUG] Link will open:', wikiUrl);
}

// ============================================
// Quiz Functions
// ============================================

function fillTopicFromSelect() {
    const select = document.getElementById('quizTopicSelect');
    const input = document.getElementById('quizTopicInput');
    if (select.value) {
        const topicName = select.options[select.selectedIndex].text;
        input.value = topicName;
    }
}

function switchQuizSource(source) {
    const topicTab = document.getElementById('topicTab');
    const pdfTab = document.getElementById('pdfTab');
    const topicSource = document.getElementById('topicSource');
    const pdfSource = document.getElementById('pdfSource');
    
    if (source === 'topic') {
        topicTab.classList.add('active');
        pdfTab.classList.remove('active');
        topicSource.classList.remove('hidden');
        pdfSource.classList.add('hidden');
    } else {
        pdfTab.classList.add('active');
        topicTab.classList.remove('active');
        pdfSource.classList.remove('hidden');
        topicSource.classList.add('hidden');
    }
}

function handlePDFUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }
    
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        alert('Please upload a PDF file');
        event.target.value = '';
        return;
    }
    
    // Update file name display
    const fileNameDisplay = document.getElementById('pdfFileName');
    fileNameDisplay.textContent = file.name;
    
    // Store file in appState
    appState.uploadedPDF = file;
    
    // Show upload status
    const statusDiv = document.getElementById('pdfUploadStatus');
    statusDiv.classList.remove('hidden');
    statusDiv.innerHTML = `<span class="upload-success">✓ PDF ready: ${file.name}</span>`;
}

async function generateQuiz() {
    // Check authentication
    if (!requireAuth('generate quizzes')) {
        return;
    }
    
    const difficultySelect = document.getElementById('difficultySelect');
    const numQuestions = parseInt(document.getElementById('numQuestions').value) || 10;
    const totalMarks = parseInt(document.getElementById('totalMarks').value) || 100;
    const marksPerQuestion = parseInt(document.getElementById('marksPerQuestion').value) || 10;
    
    // Validate: marks_per_question * no_of_questions == Total_marks
    const calculatedTotalMarks = marksPerQuestion * numQuestions;
    if (calculatedTotalMarks !== totalMarks) {
        alert(
            `Validation Error: Marks per question × Number of questions must equal Total marks.\n\n` +
            `Current values:\n` +
            `Marks per question: ${marksPerQuestion}\n` +
            `Number of questions: ${numQuestions}\n` +
            `Calculated total: ${calculatedTotalMarks}\n` +
            `Entered total marks: ${totalMarks}\n\n` +
            `Please adjust the values so that ${marksPerQuestion} × ${numQuestions} = ${totalMarks}`
        );
        return;
    }
    
    // Check if PDF is uploaded (prioritize PDF if it exists)
    const pdfTab = document.getElementById('pdfTab');
    const isPDFTabActive = pdfTab && pdfTab.classList.contains('active');
    const hasUploadedPDF = appState.uploadedPDF !== null;
    
    // Determine mode: if PDF is uploaded OR PDF tab is active, use PDF mode
    const isPDFMode = hasUploadedPDF || isPDFTabActive;
    
    let topicName = null;
    let pdfFile = null;
    
    if (isPDFMode) {
        // PDF mode - check if PDF file exists
        pdfFile = appState.uploadedPDF;
        if (!pdfFile) {
            alert('Please upload a PDF file first');
            return;
        }
        // PDF file exists, proceed with PDF generation
    } else {
        // Topic mode - only check for topic if not in PDF mode
        const topicInput = document.getElementById('quizTopicInput');
        const topicSelect = document.getElementById('quizTopicSelect');
        
        topicName = topicInput.value.trim();
        
        // If topic input is empty, try to get from select
        if (!topicName && topicSelect && topicSelect.value) {
            topicName = topicSelect.options[topicSelect.selectedIndex].text;
        }

        if (!topicName) {
            alert('Please enter or select an AI topic');
            return;
        }

        // Validate AI topic (basic check - backend will do full validation)
        const aiKeywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 
                           'neural network', 'nlp', 'natural language', 'computer vision', 
                           'reinforcement learning', 'supervised', 'unsupervised', 'transformer',
                           'cnn', 'rnn', 'lstm', 'gan', 'bert', 'gpt', 'generative'];
        const topicLower = topicName.toLowerCase();
        const isAITopic = aiKeywords.some(keyword => topicLower.includes(keyword));
        
        if (!isAITopic) {
            const confirmGenerate = confirm(
                `"${topicName}" doesn't appear to be an AI-related topic. ` +
                `Quiz generation is only available for AI topics.\n\n` +
                `Examples: Machine Learning, Deep Learning, Neural Networks, NLP, Computer Vision, etc.\n\n` +
                `Do you want to continue anyway? (Backend will validate)`
            );
            if (!confirmGenerate) {
                return;
            }
        }
    }

    const difficulty = difficultySelect.value;

    // Show loading state
    const generateBtn = document.querySelector('.action-button.primary');
    const originalText = generateBtn.innerHTML;
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span>Generating Questions...</span>';

    try {
        // Generate 2x questions for selection (as per requirement)
        const questionsToGenerate = numQuestions * 2;
        
        let response;
        
        if (isPDFMode) {
            // Upload PDF and generate quiz from it
            const formData = new FormData();
            formData.append('pdf_file', pdfFile);
            formData.append('difficulty', difficulty);
            formData.append('num_questions', questionsToGenerate.toString());
            formData.append('total_marks', totalMarks.toString());
            formData.append('marks_per_question', marksPerQuestion.toString());
            
            response = await fetch('http://localhost:5000/api/quiz/generate-from-pdf', {
                method: 'POST',
                body: formData
            });
        } else {
            // Call backend API to generate questions from topic
            response = await fetch('http://localhost:5000/api/quiz/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic: topicName,
                    difficulty: difficulty,
                    num_questions: questionsToGenerate,
                    total_marks: totalMarks,
                    marks_per_question: marksPerQuestion
                })
            });
        }

        if (!response.ok) {
            let errorMessage = `Backend error: ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // If JSON parsing fails, use status text
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        
        // Convert backend response to frontend format
        const questionPool = data.questions.map(q => ({
            id: q.id,
            question: q.question,
            type: q.type || 'short_answer',
            marks: q.marks,
            difficulty: data.difficulty
        }));

        appState.questionPool = questionPool;
        appState.selectedQuestions = [];
        appState.quizConfig = {
            topic: data.topic || 'PDF Document',
            difficulty: difficulty,
            numQuestions: numQuestions,
            totalMarks: totalMarks,
            marksPerQuestion: marksPerQuestion
        };

        // Update difficulty level based on quiz difficulty
        const difficultyMap = {
            'beginner': 'Beginner',
            'intermediate': 'Intermediate',
            'advanced': 'Advanced',
            'Beginner': 'Beginner',
            'Intermediate': 'Intermediate',
            'Advanced': 'Advanced'
        };
        const normalizedDifficulty = difficulty.toLowerCase();
        if (difficultyMap[normalizedDifficulty]) {
            appState.studentPerformance.difficultyLevel = difficultyMap[normalizedDifficulty];
            // Update performance dashboard if it's visible
            if (appState.currentSection === 'performance') {
                updatePerformanceDashboard();
            }
        }

        // Show question selection interface
        displayQuestionSelection(questionPool, numQuestions);
        document.getElementById('quizContent').classList.add('hidden');
        document.getElementById('quizResults').classList.add('hidden');
        
    } catch (error) {
        console.error('Error generating quiz:', error);
        const errorMsg = error.message.includes('AI-related') || error.message.includes('AI topic')
            ? error.message 
            : `Failed to generate quiz: ${error.message}\n\nMake sure the backend is running on http://localhost:5000`;
        alert(errorMsg);
        
        // Fallback to local generation if backend fails (only for topic mode)
        if (!isPDFMode && topicName) {
            const questionsToGenerate = numQuestions * 2;
            const questionPool = generateQuestionPool(topicName, difficulty, questionsToGenerate, marksPerQuestion);
            appState.questionPool = questionPool;
            appState.selectedQuestions = [];
            appState.quizConfig = {
                topic: topicName,
                difficulty: difficulty,
                numQuestions: numQuestions,
                totalMarks: totalMarks,
                marksPerQuestion: marksPerQuestion
            };
            
            // Update difficulty level based on quiz difficulty
            const difficultyMapFallback = {
                'beginner': 'Beginner',
                'intermediate': 'Intermediate',
                'advanced': 'Advanced',
                'Beginner': 'Beginner',
                'Intermediate': 'Intermediate',
                'Advanced': 'Advanced'
            };
            const normalizedDifficultyFallback = difficulty.toLowerCase();
            if (difficultyMapFallback[normalizedDifficultyFallback]) {
                appState.studentPerformance.difficultyLevel = difficultyMapFallback[normalizedDifficultyFallback];
                // Update performance dashboard if it's visible
                if (appState.currentSection === 'performance') {
                    updatePerformanceDashboard();
                }
            }
            
        displayQuestionSelection(questionPool, numQuestions);
        document.getElementById('quizContent').classList.add('hidden');
        document.getElementById('quizResults').classList.add('hidden');
        }
    } finally {
        // Restore button state
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalText;
    }
}


function generateQuestionPool(topicName, difficulty, count, marksPerQuestion) {
    const questions = [];
    const questionTypes = ['multiple_choice', 'true_false', 'short_answer', 'essay'];
    
    for (let i = 1; i <= count; i++) {
        const type = questionTypes[Math.floor(Math.random() * questionTypes.length)];
        let question = {
            id: i,
            question: `Question ${i}: Sample question about ${topicName} at ${difficulty} level?`,
            type: type,
            marks: marksPerQuestion,
            difficulty: difficulty
        };

        if (type === 'multiple_choice') {
            question.options = ['Option A', 'Option B', 'Option C', 'Option D'];
            question.correctAnswer = Math.floor(Math.random() * 4);
        } else if (type === 'true_false') {
            question.options = ['True', 'False'];
            question.correctAnswer = Math.floor(Math.random() * 2);
        }

        questions.push(question);
    }

    return questions;
}

function displayQuestionSelection(questionPool, requiredCount) {
    const selectionDiv = document.getElementById('questionSelection');
    const totalGenerated = document.getElementById('totalGeneratedQuestions');
    const requiredQuestions = document.getElementById('requiredQuestions');
    const selectedCount = document.getElementById('selectedCount');
    const requiredCountSpan = document.getElementById('requiredCount');
    const questionPoolDiv = document.getElementById('questionPool');

    totalGenerated.textContent = questionPool.length;
    requiredQuestions.textContent = requiredCount;
    requiredCountSpan.textContent = requiredCount;
    selectedCount.textContent = '0';

    questionPoolDiv.innerHTML = '';

    questionPool.forEach(question => {
        const item = document.createElement('div');
        item.className = 'question-pool-item';
        item.dataset.questionId = question.id;
        
        item.innerHTML = `
            <h4>${question.question}</h4>
            <p><strong>Type:</strong> ${question.type.replace('_', ' ').toUpperCase()}</p>
            <p><strong>Marks:</strong> ${question.marks}</p>
            <div class="question-meta">
                <span>Difficulty: ${question.difficulty}</span>
            </div>
        `;

        item.addEventListener('click', () => toggleQuestionSelection(question.id, item, requiredCount));
        questionPoolDiv.appendChild(item);
    });

    selectionDiv.classList.remove('hidden');
}

function toggleQuestionSelection(questionId, element, maxCount) {
    const index = appState.selectedQuestions.indexOf(questionId);
    
    if (index > -1) {
        // Deselect
        appState.selectedQuestions.splice(index, 1);
        element.classList.remove('selected');
    } else {
        // Select (if under limit)
        if (appState.selectedQuestions.length < maxCount) {
            appState.selectedQuestions.push(questionId);
            element.classList.add('selected');
        } else {
            alert(`You can only select ${maxCount} questions`);
            return;
        }
    }

    // Update UI
    document.getElementById('selectedCount').textContent = appState.selectedQuestions.length;
    const createBtn = document.getElementById('createQuizBtn');
    createBtn.disabled = appState.selectedQuestions.length !== maxCount;
}

function createQuizFromSelection() {
    if (appState.selectedQuestions.length !== appState.quizConfig.numQuestions) {
        alert(`Please select exactly ${appState.quizConfig.numQuestions} questions`);
        return;
    }

    const selectedQuestions = appState.questionPool.filter(q => 
        appState.selectedQuestions.includes(q.id)
    );

    const quiz = {
        id: `quiz_${Date.now()}`,
        topic: appState.quizConfig.topic,
        difficulty: appState.quizConfig.difficulty,
        questions: selectedQuestions,
        totalMarks: appState.quizConfig.totalMarks,
        marksPerQuestion: appState.quizConfig.marksPerQuestion
    };

    appState.currentQuiz = quiz;
    appState.quizAnswers = {};

    // Update difficulty level based on quiz difficulty
    const difficultyMap = {
        'beginner': 'Beginner',
        'intermediate': 'Intermediate',
        'advanced': 'Advanced',
        'Beginner': 'Beginner',
        'Intermediate': 'Intermediate',
        'Advanced': 'Advanced'
    };
    const normalizedDifficulty = quiz.difficulty.toLowerCase();
    if (difficultyMap[normalizedDifficulty]) {
        appState.studentPerformance.difficultyLevel = difficultyMap[normalizedDifficulty];
        // Update performance dashboard if it's visible
        if (appState.currentSection === 'performance') {
            updatePerformanceDashboard();
        }
    }

    // Hide selection, show quiz
    document.getElementById('questionSelection').classList.add('hidden');
    displayQuiz(quiz);
    document.getElementById('quizResults').classList.add('hidden');
}

function generateQuestions(topicId, difficulty) {
    // Sample questions based on topic and difficulty
    const questionSets = {
        1: {
            Beginner: [
                {
                    id: 1,
                    question: "What is the output of: print(2 + 3 * 4)?",
                    type: "multiple_choice",
                    options: ["14", "20", "11", "24"],
                    correctAnswer: 0
                },
                {
                    id: 2,
                    question: "Which keyword is used to define a function in Python?",
                    type: "multiple_choice",
                    options: ["function", "def", "define", "func"],
                    correctAnswer: 1
                }
            ],
            Intermediate: [
                {
                    id: 1,
                    question: "What is the difference between a list and a tuple?",
                    type: "text",
                    correctAnswer: null
                },
                {
                    id: 2,
                    question: "Explain list comprehension with an example.",
                    type: "text",
                    correctAnswer: null
                }
            ],
            Advanced: [
                {
                    id: 1,
                    question: "Implement a decorator that measures function execution time.",
                    type: "text",
                    correctAnswer: null
                }
            ]
        }
    };

    const questions = questionSets[topicId]?.[difficulty] || questionSets[1][difficulty] || questionSets[1]['Beginner'];
    return questions;
}

function displayQuiz(quiz) {
    const quizContent = document.getElementById('quizContent');
    const quizTitle = document.getElementById('quizTitle');
    const quizDifficulty = document.getElementById('quizDifficulty');
    const questionCount = document.getElementById('questionCount');
    const quizMarks = document.getElementById('quizMarks');
    const quizQuestions = document.getElementById('quizQuestions');
    const submitButton = document.querySelector('.submit-quiz');

    quizTitle.textContent = `Quiz: ${quiz.topic}`;
    quizDifficulty.textContent = quiz.difficulty;
    questionCount.textContent = `${quiz.questions.length} Questions`;
    quizMarks.textContent = `Total: ${quiz.totalMarks} Marks`;

    quizQuestions.innerHTML = '';
    quiz.questions.forEach((question, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'question-card';
        questionCard.innerHTML = `
            <div class="question-header">
                <div class="question-text">Question ${index + 1}: ${question.question}</div>
                <div class="question-marks-badge">${question.marks} Marks</div>
            </div>
            ${question.type === 'multiple_choice' || question.type === 'true_false'
                ? generateMultipleChoiceOptions(question, index)
                : generateTextAnswer(question, index)
            }
        `;
        quizQuestions.appendChild(questionCard);
    });

    quizContent.classList.remove('hidden');
    submitButton.style.display = 'block';

    // Add event listeners for options
    document.querySelectorAll('.option-item').forEach(item => {
        item.addEventListener('click', function() {
            const questionId = parseInt(this.dataset.questionId);
            const optionIndex = parseInt(this.dataset.optionIndex);
            
            // Remove previous selection
            document.querySelectorAll(`[data-question-id="${questionId}"]`).forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Select current option
            this.classList.add('selected');
            appState.quizAnswers[questionId] = optionIndex;
        });
    });
}

function generateMultipleChoiceOptions(question, index) {
    let html = '<div class="options-list">';
    question.options.forEach((option, optIndex) => {
        html += `
            <div class="option-item" data-question-id="${question.id}" data-option-index="${optIndex}">
                ${option}
            </div>
        `;
    });
    html += '</div>';
    return html;
}

function printQuiz() {
    // Hide elements that shouldn't be printed
    const submitButton = document.querySelector('.submit-quiz');
    const quizActions = document.querySelector('.quiz-actions');
    
    const originalStyles = {
        submitButton: submitButton ? submitButton.style.display : 'none',
        quizActions: quizActions ? quizActions.style.display : 'none'
    };
    
    if (submitButton) submitButton.style.display = 'none';
    if (quizActions) quizActions.style.display = 'none';
    
    // Create print styles
    const printStyles = `
        <style>
            @media print {
                body * {
                    visibility: hidden;
                }
                .quiz-content, .quiz-content * {
                    visibility: visible;
                }
                .quiz-content {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 100%;
                }
                .quiz-actions, .submit-quiz {
                    display: none !important;
                }
                .question-card {
                    page-break-inside: avoid;
                    margin-bottom: 1.5rem;
                }
                .option-item {
                    page-break-inside: avoid;
                }
            }
        </style>
    `;
    
    // Add print styles temporarily
    const styleSheet = document.createElement("style");
    styleSheet.textContent = printStyles;
    document.head.appendChild(styleSheet);
    
    // Trigger print
    window.print();
    
    // Remove print styles and restore elements
    setTimeout(() => {
        document.head.removeChild(styleSheet);
        if (submitButton) submitButton.style.display = originalStyles.submitButton;
        if (quizActions) quizActions.style.display = originalStyles.quizActions;
    }, 1000);
}

async function downloadQuizPDF() {
    // Check if quiz exists
    if (!appState.currentQuiz) {
        alert('No quiz found. Please generate a quiz first.');
        return;
    }
    
    // Check if jsPDF is available
    let jsPDF_constructor;
    if (typeof window.jsPDF !== 'undefined') {
        // Direct access - window.jsPDF is the constructor
        jsPDF_constructor = window.jsPDF;
    } else if (typeof window.jspdf !== 'undefined') {
        // UMD bundle access
        if (typeof window.jspdf.jsPDF !== 'undefined') {
            jsPDF_constructor = window.jspdf.jsPDF;
        } else if (typeof window.jspdf.default !== 'undefined') {
            jsPDF_constructor = window.jspdf.default;
        } else {
            // Try as direct constructor
            jsPDF_constructor = window.jspdf;
        }
    } else {
        alert('PDF library not loaded. Please refresh the page and try again.');
        console.error('jsPDF not found. Available globals:', Object.keys(window).filter(k => k.toLowerCase().includes('pdf')));
        return;
    }
    
    // Verify it's a constructor
    if (typeof jsPDF_constructor !== 'function') {
        alert('PDF library error: jsPDF constructor not found. Please refresh the page.');
        console.error('jsPDF_constructor is not a function:', typeof jsPDF_constructor, jsPDF_constructor);
        return;
    }
    
    const quiz = appState.currentQuiz;
    
        // Show loading message
    const loadingMsg = document.createElement('div');
        loadingMsg.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.8); color: white; padding: 20px; border-radius: 10px; z-index: 10000;';
        loadingMsg.textContent = 'Generating PDF...';
        document.body.appendChild(loadingMsg);
        
    try {
        // Create new jsPDF instance - use the constructor directly
        const doc = new jsPDF_constructor({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });
        
        // Set font
        doc.setFont('helvetica');
        
        // Initial position
        let y = 20; // Start 20mm from top
        const margin = 15; // Left margin
        const maxWidth = doc.internal.pageSize.width - 2 * margin; // Page width minus margins
        const lineHeight = 7; // Line spacing
        
        // Add Quiz Title
        doc.setFontSize(18);
        doc.setFont('helvetica', 'bold');
        const title = `Quiz: ${quiz.topic}`;
        doc.text(title, margin, y);
        y += lineHeight * 1.5;
        
        // Add Quiz Metadata
        doc.setFontSize(12);
        doc.setFont('helvetica', 'normal');
        doc.text(`Difficulty: ${quiz.difficulty}`, margin, y);
        y += lineHeight;
        doc.text(`Questions: ${quiz.questions.length}`, margin, y);
        y += lineHeight;
        doc.text(`Total Marks: ${quiz.totalMarks}`, margin, y);
        y += lineHeight * 2;
        
        // Add each question as a string - one by one
        quiz.questions.forEach((question, index) => {
            // Check if we need a new page
            if (y > doc.internal.pageSize.height - 30) {
                doc.addPage();
                y = margin;
            }
            
            // Question number and text - stored as string
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            const questionText = `Question ${index + 1}: ${question.question}`;
            const splitQuestion = doc.splitTextToSize(questionText, maxWidth);
            doc.text(splitQuestion, margin, y);
            y += splitQuestion.length * lineHeight;
            
            // Marks
            doc.setFontSize(11);
            doc.setFont('helvetica', 'normal');
            doc.text(`[${question.marks} Marks]`, margin, y);
            y += lineHeight * 1.2;
            
            // Options for multiple choice or true/false - stored as strings
            if (question.type === 'multiple_choice' || question.type === 'true_false') {
                if (question.options && question.options.length > 0) {
                    doc.setFontSize(11);
                    question.options.forEach((option, optIndex) => {
                        const optionLabel = String.fromCharCode(65 + optIndex); // A, B, C, D...
                        const optionText = `${optionLabel}. ${option}`;
                        const splitOption = doc.splitTextToSize(optionText, maxWidth - 10);
                        doc.text(splitOption, margin + 5, y);
                        y += splitOption.length * lineHeight;
                    });
                }
            } else {
                // For text/short answer questions, add blank lines
                doc.setFontSize(11);
                doc.text('Answer: ____________________________________________________', margin + 5, y);
                y += lineHeight;
                doc.text('____________________________________________________________', margin + 5, y);
                y += lineHeight;
            }
            
            // Add spacing between questions
            y += lineHeight * 1.5;
        });
        
        // Generate filename and save
        const filename = `Quiz_${quiz.topic.replace(/[^a-z0-9]/gi, '_')}_${new Date().getTime()}.pdf`;
        doc.save(filename);
        
        // Remove loading message
        if (loadingMsg && document.body.contains(loadingMsg)) {
            document.body.removeChild(loadingMsg);
        }
        
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Error generating PDF: ' + error.message);
        
        // Remove loading message if still present
        if (loadingMsg && document.body.contains(loadingMsg)) {
            document.body.removeChild(loadingMsg);
        }
    }
}

function generateTextAnswer(question, index) {
    return `
        <textarea 
            class="text-answer" 
            id="text_answer_${question.id}"
            placeholder="Type your answer here..."
            oninput="appState.quizAnswers[${question.id}] = this.value"
        ></textarea>
    `;
}

async function submitQuiz() {
    // Check authentication
    if (!requireAuth('submit quizzes')) {
        return;
    }
    
    if (!appState.currentQuiz) {
        alert('No quiz to submit');
        return;
    }

    const quiz = appState.currentQuiz;
    
    // Show loading
    const submitBtn = document.querySelector('.submit-quiz');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Evaluating Quiz...</span>';

    try {
        // Prepare answers - include all questions (empty string if not answered)
        const answers = {};
        quiz.questions.forEach(question => {
            const answer = appState.quizAnswers[question.id] || "";
            answers[question.id] = answer.trim();
        });

        // Call backend API to evaluate
        const response = await fetch('http://localhost:5000/api/quiz/evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quiz_id: quiz.id,
                answers: answers,
                questions: quiz.questions,
                topic: quiz.topic,
                difficulty: quiz.difficulty,
                marks_per_question: quiz.marksPerQuestion || 10,
                user_id: "default",
                time_taken_seconds: 0
            })
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const result = await response.json();
        
        // Update performance
        appState.studentPerformance.totalQuizzes++;
        appState.studentPerformance.correctAnswers += result.correct_answers;
        appState.studentPerformance.averageScore = 
            (appState.studentPerformance.correctAnswers / 
             (appState.studentPerformance.totalQuizzes * result.total_questions)) * 100;
        
        // Normalize quiz difficulty level (Beginner, Intermediate, Advanced)
        let normalizedDifficulty = quiz.difficulty;
        if (quiz.difficulty) {
            const diffLower = quiz.difficulty.toLowerCase();
            if (diffLower === 'beginner') {
                normalizedDifficulty = 'Beginner';
            } else if (diffLower === 'intermediate') {
                normalizedDifficulty = 'Intermediate';
            } else if (diffLower === 'advanced') {
                normalizedDifficulty = 'Advanced';
            }
        } else {
            normalizedDifficulty = 'Beginner';
        }
        
        // Update difficulty level based on the quiz difficulty (not average score)
        // This ensures that if you complete an advanced quiz, your level becomes Advanced
        appState.studentPerformance.difficultyLevel = normalizedDifficulty;
        
        // Also update performance dashboard if it's visible
        if (appState.currentSection === 'performance') {
            updatePerformanceDashboard();
        }

        // Add to performance history
        
        appState.studentPerformance.performanceHistory.push({
            date: new Date().toISOString(),
            score: result.score,
            topic: quiz.topic,
            difficulty: normalizedDifficulty || 'Beginner'
        });

        // Display results with detailed feedback
        displayQuizResults(result.score, result.correct_answers, result.total_questions, result.feedback);
        
        // Hide quiz content
        submitBtn.style.display = 'none';
        
    } catch (error) {
        console.error('Error evaluating quiz:', error);
        alert(`Failed to evaluate quiz: ${error.message}\n\nMake sure the backend is running on http://localhost:5000`);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

function displayQuizResults(score, correctCount, totalQuestions, feedback = null) {
    const resultsDiv = document.getElementById('quizResults');
    const finalScore = document.getElementById('finalScore');
    const resultsFeedback = document.getElementById('resultsFeedback');

    finalScore.textContent = `${score.toFixed(1)}%`;
    
    let feedbackHTML = `
        <p><strong>Correct Answers:</strong> ${correctCount} out of ${totalQuestions}</p>
        <p>${score >= 80 ? 'Excellent work! 🎉' : score >= 60 ? 'Good job! Keep practicing! 💪' : 'Keep learning! You\'re improving! 📚'}</p>
    `;
    
    // Add detailed feedback if available
    if (feedback && feedback.length > 0) {
        feedbackHTML += '<div class="detailed-feedback" style="margin-top: 20px; padding: 15px; background: #f8fafc; border-radius: 8px;">';
        feedbackHTML += '<h4 style="margin-bottom: 10px;">Question-wise Feedback:</h4>';
        feedback.forEach((item, index) => {
            const status = item.correct ? '✅' : '❌';
            const marksDisplay = `${item.marks_awarded}/${item.max_marks}`;
            feedbackHTML += `
                <div style="margin-bottom: 10px; padding: 10px; background: white; border-radius: 5px;">
                    <strong>Q${index + 1}:</strong> ${status} ${marksDisplay} marks
                    <br><small style="color: #64748b;">${item.feedback}</small>
                </div>
            `;
        });
        feedbackHTML += '</div>';
    }
    
    resultsFeedback.innerHTML = feedbackHTML;
    resultsDiv.classList.remove('hidden');

    // Confetti effect
    createConfetti();
}

function createConfetti() {
    // Simple confetti effect
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const confetti = document.createElement('div');
            confetti.style.position = 'fixed';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.top = '-10px';
            confetti.style.width = '10px';
            confetti.style.height = '10px';
            confetti.style.backgroundColor = ['#667eea', '#764ba2', '#4facfe', '#f5576c'][Math.floor(Math.random() * 4)];
            confetti.style.borderRadius = '50%';
            confetti.style.pointerEvents = 'none';
            confetti.style.zIndex = '9999';
            confetti.style.animation = 'confettiFall 3s linear forwards';
            document.body.appendChild(confetti);

            setTimeout(() => confetti.remove(), 3000);
        }, i * 50);
    }
}

// Add confetti animation to CSS dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes confettiFall {
        to {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================
// Performance Functions
// ============================================

function updatePerformanceDashboard() {
    const perf = appState.studentPerformance;

    document.getElementById('totalQuizzes').textContent = perf.totalQuizzes;
    document.getElementById('averageScore').textContent = `${perf.averageScore.toFixed(1)}%`;
    document.getElementById('correctAnswers').textContent = Math.round(perf.correctAnswers);
    document.getElementById('difficultyLevel').textContent = perf.difficultyLevel;

    // Update performance chart
    updatePerformanceChart();

    // Update difficulty chart
    updateDifficultyChart();
}

function updatePerformanceChart() {
    const canvas = document.getElementById('performanceChart');
    if (!canvas) {
        // Canvas not found, might not be initialized yet
        return;
    }

    // Ensure canvas has proper dimensions
    if (canvas.width === 0 || canvas.height === 0) {
        canvas.width = canvas.offsetWidth || 800;
        canvas.height = 300;
    }

    const ctx = canvas.getContext('2d');
    const history = appState.studentPerformance.performanceHistory;
    
    let data;
    let hasHistory = false;
    if (history.length === 0) {
        // Show sample data with current average
        const sampleData = [60, 65, 70, 75, 80, 75, 85, 90, 85];
        if (appState.studentPerformance.averageScore > 0) {
            sampleData.push(appState.studentPerformance.averageScore);
        }
        data = sampleData;
    } else {
        data = history.map(h => h.score);
        hasHistory = true;
    }
    
    drawPerformanceChart(ctx, data, hasHistory ? history : null);
}

function drawPerformanceChart(ctx, data, history = null) {
    const width = ctx.canvas.width;
    const height = ctx.canvas.height;
    const padding = 50;
    const chartWidth = width - 2 * padding;
    const chartHeight = height - 2 * padding;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Find min and max for better scaling
    const minValue = Math.max(0, Math.min(...data) - 10);
    const maxValue = Math.min(100, Math.max(...data) + 10);
    const range = maxValue - minValue || 100;

    // Draw background
    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, width, height);

    // Draw grid lines and Y-axis labels
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.font = '12px Inter, sans-serif';
    ctx.fillStyle = '#64748b';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    const gridLines = 5;
    for (let i = 0; i <= gridLines; i++) {
        const y = padding + (chartHeight / gridLines) * i;
        const value = maxValue - (range / gridLines) * i;
        
        // Draw grid line
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
        
        // Draw Y-axis label
        ctx.fillText(`${Math.round(value)}%`, padding - 10, y);
    }

    // Draw X-axis labels (quiz numbers or dates)
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#64748b';
    
    if (data.length === 0) {
        ctx.fillText('No data available', width / 2, height / 2);
        return;
    }
    
    const stepX = chartWidth / Math.max(1, data.length - 1);
    data.forEach((value, index) => {
        const x = padding + stepX * index;
        
        // Label
        if (history && history[index]) {
            const date = new Date(history[index].date);
            ctx.fillText(`Q${index + 1}`, x, height - padding + 5);
            ctx.font = '10px Inter, sans-serif';
            ctx.fillText(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), x, height - padding + 20);
            ctx.font = '12px Inter, sans-serif';
        } else {
            ctx.fillText(`Q${index + 1}`, x, height - padding + 10);
        }
    });

    // Draw area under curve (gradient)
    if (data.length > 1) {
        const gradient = ctx.createLinearGradient(padding, padding, padding, padding + chartHeight);
        gradient.addColorStop(0, 'rgba(102, 126, 234, 0.3)');
        gradient.addColorStop(1, 'rgba(102, 126, 234, 0.05)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.moveTo(padding, padding + chartHeight);
        
        data.forEach((value, index) => {
            const x = padding + stepX * index;
            const normalizedValue = (value - minValue) / range;
            const y = padding + chartHeight - (normalizedValue * chartHeight);
            ctx.lineTo(x, y);
        });
        
        ctx.lineTo(padding + stepX * (data.length - 1), padding + chartHeight);
        ctx.closePath();
        ctx.fill();
    }

    // Draw line
    ctx.strokeStyle = '#667eea';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    data.forEach((value, index) => {
        const x = padding + stepX * index;
        const normalizedValue = (value - minValue) / range;
        const y = padding + chartHeight - (normalizedValue * chartHeight);
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();

    // Draw points
    ctx.fillStyle = '#667eea';
    data.forEach((value, index) => {
        const x = padding + stepX * index;
        const normalizedValue = (value - minValue) / range;
        const y = padding + chartHeight - (normalizedValue * chartHeight);
        
        // Outer circle
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        
        // Inner circle
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#667eea';
        ctx.fill();
        
        // Value label on hover area (optional, can be enhanced with hover detection)
    });

    // Draw title/labels
    ctx.fillStyle = '#1e293b';
    ctx.font = 'bold 14px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText('Score (%)', 20, 10);
}

function updateDifficultyChart() {
    const chartDiv = document.getElementById('difficultyChart');
    if (!chartDiv) return;

    const history = appState.studentPerformance.performanceHistory;
    const currentDifficulty = appState.studentPerformance.difficultyLevel;
    const levels = ['Beginner', 'Intermediate', 'Advanced'];
    
    // Count quizzes by difficulty level from history
    const difficultyCounts = {
        'Beginner': 0,
        'Intermediate': 0,
        'Advanced': 0
    };
    
    // Count from history if available
    if (history && history.length > 0) {
        // Count quizzes by their actual difficulty level
        history.forEach(item => {
            // Use stored difficulty if available, otherwise fallback to score-based classification
            if (item.difficulty) {
                const diff = item.difficulty;
                // Normalize difficulty level
                if (diff === 'Beginner' || diff.toLowerCase() === 'beginner') {
                    difficultyCounts['Beginner']++;
                } else if (diff === 'Intermediate' || diff.toLowerCase() === 'intermediate') {
                    difficultyCounts['Intermediate']++;
                } else if (diff === 'Advanced' || diff.toLowerCase() === 'advanced') {
                    difficultyCounts['Advanced']++;
                } else {
                    // Fallback: count as Beginner if difficulty is unknown
                    difficultyCounts['Beginner']++;
                }
            } else {
                // Fallback to score-based classification for old entries without difficulty
                if (item.score >= 80) {
                    difficultyCounts['Advanced']++;
                } else if (item.score >= 60) {
                    difficultyCounts['Intermediate']++;
                } else {
                    difficultyCounts['Beginner']++;
                }
            }
        });
    }
    
    // Calculate total for percentage
    const totalQuizzes = Object.values(difficultyCounts).reduce((sum, count) => sum + count, 0);
    const maxCount = Math.max(...Object.values(difficultyCounts), 1);
    
    chartDiv.innerHTML = '';
    
    // Add chart title/header
    const header = document.createElement('div');
    header.style.cssText = 'margin-bottom: 1rem; font-weight: 600; color: #1e293b; font-size: 14px;';
    header.textContent = 'Quizzes by Difficulty Level';
    chartDiv.appendChild(header);
    
    // Create progression visualization
    levels.forEach(level => {
        const barDiv = document.createElement('div');
        barDiv.className = 'difficulty-bar';
        barDiv.style.cssText = 'margin-bottom: 1rem;';
        
        const labelRow = document.createElement('div');
        labelRow.style.cssText = 'display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;';
        
        const label = document.createElement('div');
        label.className = 'difficulty-label';
        label.style.cssText = 'font-weight: 500; color: #1e293b;';
        label.textContent = level;
        
        const countLabel = document.createElement('div');
        countLabel.style.cssText = 'font-size: 0.875rem; color: #64748b;';
        const count = difficultyCounts[level];
        const percentage = totalQuizzes > 0 ? ((count / totalQuizzes) * 100).toFixed(0) : 0;
        countLabel.textContent = `${count} quiz${count !== 1 ? 'zes' : ''} (${percentage}%)`;
        if (level === currentDifficulty) {
            countLabel.innerHTML += ' <span style="color: #667eea; font-weight: 600;">● Current</span>';
        }
        
        labelRow.appendChild(label);
        labelRow.appendChild(countLabel);
        
        const progress = document.createElement('div');
        progress.className = 'difficulty-progress';
        progress.style.cssText = 'width: 100%; height: 32px; background: #e2e8f0; border-radius: 8px; overflow: hidden; position: relative;';
        
        const fill = document.createElement('div');
        fill.className = `difficulty-fill ${level.toLowerCase()}`;
        const fillWidth = maxCount > 0 ? (count / maxCount) * 100 : 0;
        fill.style.width = `${fillWidth}%`;
        fill.style.height = '100%';
        fill.style.transition = 'width 0.3s ease';
        fill.style.display = 'flex';
        fill.style.alignItems = 'center';
        fill.style.paddingLeft = '12px';
        fill.style.fontSize = '0.875rem';
        fill.style.fontWeight = '600';
        fill.style.color = '#ffffff';
        
        // Set colors based on difficulty level
        if (level === 'Beginner') {
            fill.style.background = 'linear-gradient(90deg, #10b981, #059669)';
        } else if (level === 'Intermediate') {
            fill.style.background = 'linear-gradient(90deg, #f59e0b, #d97706)';
        } else {
            fill.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
        }
        
        if (count > 0) {
            fill.textContent = `${count}`;
        }
        
        progress.appendChild(fill);
        barDiv.appendChild(labelRow);
        barDiv.appendChild(progress);
        chartDiv.appendChild(barDiv);
    });
    
    // Add summary if no data
    if (totalQuizzes === 0) {
        const noDataMsg = document.createElement('div');
        noDataMsg.style.cssText = 'text-align: center; color: #64748b; padding: 2rem; font-style: italic;';
        noDataMsg.textContent = 'Complete quizzes to see your difficulty progression';
        chartDiv.appendChild(noDataMsg);
    } else {
        // Add progression indicator
        const progressionDiv = document.createElement('div');
        progressionDiv.style.cssText = 'margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e2e8f0;';
        
        const progressionText = document.createElement('div');
        progressionText.style.cssText = 'font-size: 0.875rem; color: #64748b; text-align: center;';
        
        const levelIndex = levels.indexOf(currentDifficulty);
        const progressionIcon = levelIndex === 0 ? '📚' : levelIndex === 1 ? '📖' : '🎓';
        progressionText.innerHTML = `${progressionIcon} <strong style="color: #1e293b;">Current Level: ${currentDifficulty}</strong>`;
        
        progressionDiv.appendChild(progressionText);
        chartDiv.appendChild(progressionDiv);
    }
}

// ============================================
// Study Path Functions
// ============================================

function togglePathTopicMode() {
    const customInput = document.getElementById('pathCustomInput');
    const predefinedSelect = document.getElementById('pathPredefinedSelect');
    const mode = document.querySelector('input[name="pathTopicMode"]:checked').value;

    if (mode === 'custom') {
        customInput.classList.remove('hidden');
        predefinedSelect.classList.add('hidden');
    } else {
        customInput.classList.add('hidden');
        predefinedSelect.classList.remove('hidden');
    }
}

async function generateStudyPath() {
    // Check authentication
    if (!requireAuth('generate study paths')) {
        return;
    }
    
    const mode = document.querySelector('input[name="pathTopicMode"]:checked').value;
    const difficulty = document.querySelector('input[name="pathDifficulty"]:checked').value;
    let topicName = '';

    if (mode === 'custom') {
        const customInput = document.getElementById('pathCustomTopic');
        topicName = customInput.value.trim();
        
        if (!topicName) {
            alert('Please enter a topic');
            return;
        }
    } else {
        const topicSelect = document.getElementById('pathTopicSelect');
        const topicId = parseInt(topicSelect.value);

        if (!topicId) {
            alert('Please select a topic');
            return;
        }

        const explanation = topicExplanations[topicId];
        if (!explanation) {
            alert('Topic not found');
            return;
        }
        topicName = explanation.title;
    }

    // Show loading state
    const pathContent = document.getElementById('studyPathContent');
    const pathSteps = document.getElementById('pathSteps');
    pathSteps.innerHTML = '<div class="loading-message">Generating study path...</div>';
    pathContent.classList.remove('hidden');

    // Generate detailed roadmap structure based on difficulty
    let roadmap = [];
    
    if (difficulty === 'beginner') {
        roadmap = [
            {
                phase: 'Foundation',
                phaseNumber: 1,
                milestones: [
                    { id: 1, title: 'Introduction & Background', description: 'Understand what ' + topicName + ' is, its history, and why it matters', time: '1 hour', status: 'pending', objectives: ['Learn the basic concept', 'Understand historical context', 'Identify key importance'] },
                    { id: 2, title: 'Core Definition', description: 'Master the fundamental definition and essential characteristics', time: '1 hour', status: 'pending', objectives: ['Define core concepts', 'Identify key properties', 'Understand basic terminology'] }
                ]
            },
            {
                phase: 'Learning & Practice',
                phaseNumber: 2,
                milestones: [
                    { id: 3, title: 'Examples & Use Cases', description: 'Explore concrete examples and real-world scenarios', time: '2 hours', status: 'pending', objectives: ['Study practical examples', 'Analyze use cases', 'Understand applications'] },
                    { id: 4, title: 'Applications', description: 'Discover where and how ' + topicName + ' is used in the real world', time: '2 hours', status: 'pending', objectives: ['Identify industry applications', 'Explore practical uses', 'Understand real-world impact'] },
                    { id: 5, title: 'Practice Problems', description: 'Solve exercises and problems to reinforce learning', time: '2 hours', status: 'pending', objectives: ['Complete practice exercises', 'Solve basic problems', 'Apply learned concepts'] }
                ]
            }
        ];
    } else if (difficulty === 'intermediate') {
        roadmap = [
            {
                phase: 'Foundation',
                phaseNumber: 1,
                milestones: [
                    { id: 1, title: 'Introduction & Background', description: 'Deep dive into ' + topicName + ' origins, evolution, and significance', time: '1 hour', status: 'pending', objectives: ['Understand historical development', 'Learn key milestones', 'Identify significance'] },
                    { id: 2, title: 'Core Definition', description: 'Master precise definitions and fundamental principles', time: '1 hour', status: 'pending', objectives: ['Define core principles', 'Understand core terminology', 'Identify essential characteristics'] }
                ]
            },
            {
                phase: 'Deep Understanding',
                phaseNumber: 2,
                milestones: [
                    { id: 3, title: 'Detailed Explanation', description: 'Comprehensive understanding of how ' + topicName + ' works with 5 detailed sections', time: '3 hours', status: 'pending', objectives: ['Understand mechanisms', 'Learn key principles', 'Master technical details', 'Grasp relationships', 'Appreciate importance'] }
                ]
            },
            {
                phase: 'Application & Mastery',
                phaseNumber: 3,
                milestones: [
                    { id: 4, title: 'Examples & Use Cases', description: 'Analyze complex examples and advanced use cases', time: '2 hours', status: 'pending', objectives: ['Study advanced examples', 'Analyze complex scenarios', 'Understand patterns'] },
                    { id: 5, title: 'Real-World Applications', description: 'Explore industry applications and practical implementations', time: '2 hours', status: 'pending', objectives: ['Identify industry uses', 'Understand implementation', 'Analyze case studies'] },
                    { id: 6, title: 'Practice Problems', description: 'Solve intermediate-level problems and challenges', time: '3 hours', status: 'pending', objectives: ['Solve intermediate problems', 'Apply advanced concepts', 'Build problem-solving skills'] }
                ]
            }
        ];
    } else if (difficulty === 'advanced') {
        roadmap = [
            {
                phase: 'Foundation',
                phaseNumber: 1,
                milestones: [
                    { id: 1, title: 'Introduction & Background', description: 'Comprehensive overview of ' + topicName + ' evolution and current state', time: '1 hour', status: 'pending', objectives: ['Understand complete history', 'Learn current state', 'Identify research directions'] },
                    { id: 2, title: 'Core Definition', description: 'Master advanced definitions and theoretical foundations', time: '1 hour', status: 'pending', objectives: ['Master theoretical foundations', 'Understand advanced terminology', 'Grasp complex definitions'] }
                ]
            },
            {
                phase: 'Deep Understanding',
                phaseNumber: 2,
                milestones: [
                    { id: 3, title: 'Comprehensive Explanation', description: 'In-depth technical understanding of mechanisms and processes', time: '3 hours', status: 'pending', objectives: ['Master technical mechanisms', 'Understand complex processes', 'Grasp advanced principles'] }
                ]
            },
            {
                phase: 'Application & Analysis',
                phaseNumber: 3,
                milestones: [
                    { id: 4, title: 'Advanced Examples', description: 'Study cutting-edge examples and complex implementations', time: '2 hours', status: 'pending', objectives: ['Analyze advanced examples', 'Study complex implementations', 'Understand edge cases'] },
                    { id: 5, title: 'Industry Applications', description: 'Explore advanced applications and innovative uses', time: '2 hours', status: 'pending', objectives: ['Study innovative applications', 'Analyze industry trends', 'Understand future potential'] },
                    { id: 6, title: 'Complex Problems', description: 'Solve advanced problems and research-level challenges', time: '3 hours', status: 'pending', objectives: ['Solve complex problems', 'Tackle research challenges', 'Develop advanced skills'] }
                ]
            },
            {
                phase: 'Expertise & Research',
                phaseNumber: 4,
                milestones: [
                    { id: 7, title: 'Advanced Related Concepts', description: 'Explore cutting-edge developments and related research areas', time: '4 hours', status: 'pending', objectives: ['Study advanced theories', 'Explore research areas', 'Understand state-of-the-art'] },
                    { id: 8, title: 'Advanced Problem Solving', description: 'Master research-level problems and complex scenarios', time: '4 hours', status: 'pending', objectives: ['Solve research problems', 'Develop expert skills', 'Master complex scenarios'] },
                    { id: 9, title: 'Research Papers & Literature', description: 'Review academic papers and scholarly resources', time: '3 hours', status: 'pending', objectives: ['Read key research papers', 'Understand academic literature', 'Identify research gaps'] }
                ]
            }
        ];
    }

    appState.studyPath = roadmap;
    displayStudyPath(roadmap);
}

function displayStudyPath(roadmap) {
    const pathSteps = document.getElementById('pathSteps');
    const pathContent = document.getElementById('studyPathContent');

    pathSteps.innerHTML = '';
    
    roadmap.forEach((phase, phaseIndex) => {
        const phaseDiv = document.createElement('div');
        phaseDiv.className = 'roadmap-phase';
        phaseDiv.setAttribute('data-phase-index', phaseIndex);
        
        // Calculate phase progress
        const totalMilestones = phase.milestones.length;
        const completedMilestones = phase.milestones.filter(m => m.status === 'completed').length;
        const progressPercent = totalMilestones > 0 ? (completedMilestones / totalMilestones) * 100 : 0;
        
        let milestonesHTML = '';
        phase.milestones.forEach((milestone, milestoneIndex) => {
            const statusClass = milestone.status === 'completed' ? 'completed' : milestone.status === 'in-progress' ? 'in-progress' : 'pending';
            const statusIcon = milestone.status === 'completed' ? '✓' : milestone.status === 'in-progress' ? '⟳' : '○';
            const globalIndex = phase.milestones.slice(0, milestoneIndex).reduce((sum, m) => sum + 1, 0) + milestoneIndex;
            
            const objectivesHTML = milestone.objectives.map(obj => 
                `<li class="objective-item">${obj}</li>`
            ).join('');
            
            milestonesHTML += `
                <div class="roadmap-milestone ${statusClass}" data-milestone-id="${milestone.id}">
                    <div class="milestone-header">
                        <div class="milestone-number">${milestone.id}</div>
                        <div class="milestone-content">
                            <h4 class="milestone-title">${milestone.title}</h4>
                            <p class="milestone-description">${milestone.description}</p>
                        </div>
                        <div class="milestone-status ${statusClass}">
                            <span class="status-icon">${statusIcon}</span>
                            <span class="status-text">${milestone.status}</span>
                        </div>
                    </div>
                    <div class="milestone-details">
                        <div class="milestone-meta">
                            <span class="time-estimate">⏱️ ${milestone.time}</span>
                        </div>
                        <div class="milestone-objectives">
                            <h5>Learning Objectives:</h5>
                            <ul class="objectives-list">
                                ${objectivesHTML}
                            </ul>
                        </div>
                        <div class="milestone-actions">
                            <button class="milestone-action-btn ${statusClass}" onclick="toggleMilestoneStatus(${phaseIndex}, ${milestoneIndex})">
                                ${milestone.status === 'completed' ? '✓ Completed' : 'Mark as Done'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        phaseDiv.innerHTML = `
            <div class="phase-header">
                <div class="phase-info">
                    <h3 class="phase-title">Phase ${phase.phaseNumber}: ${phase.phase}</h3>
                    <div class="phase-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progressPercent}%"></div>
                        </div>
                        <span class="progress-text">${completedMilestones}/${totalMilestones} milestones completed</span>
                    </div>
                </div>
            </div>
            <div class="phase-milestones">
                ${milestonesHTML}
            </div>
        `;
        
        pathSteps.appendChild(phaseDiv);
    });

    pathContent.classList.remove('hidden');
}

function toggleMilestoneStatus(phaseIndex, milestoneIndex) {
    if (!appState.studyPath || phaseIndex < 0 || phaseIndex >= appState.studyPath.length) {
        return;
    }
    
    const phase = appState.studyPath[phaseIndex];
    if (milestoneIndex < 0 || milestoneIndex >= phase.milestones.length) {
        return;
    }
    
    const milestone = phase.milestones[milestoneIndex];
    
    // Toggle between pending and completed
    if (milestone.status === 'completed') {
        milestone.status = 'pending';
    } else {
        milestone.status = 'completed';
    }
    
    // Update the display
    displayStudyPath(appState.studyPath);
}

// ============================================
// Chat Functions
// ============================================

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addChatMessage('user', message);
    input.value = '';

    // Show loading indicator
    const loadingMessageId = 'loading-' + Date.now();
    addChatMessage('assistant', 'Thinking...', loadingMessageId);

    try {
        // Call backend API for chat
        const response = await fetch('http://localhost:5000/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: 'default'
            })
        });

        if (!response.ok) {
            throw new Error(`Backend error: ${response.statusText}`);
        }

        const data = await response.json();
        
        // Remove loading message
        removeChatMessage(loadingMessageId);
        
        // Add AI response from backend
        const aiResponse = data.message || data.response || 'I apologize, but I couldn\'t generate a response.';
        addChatMessage('assistant', aiResponse);
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Remove loading message
        removeChatMessage(loadingMessageId);
        
        // Show error message
        addChatMessage('assistant', `Sorry, I encountered an error: ${error.message}. Please make sure the backend is running on http://localhost:5000`);
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type - now includes images
    const allowedTypes = ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain',
                          'image/jpeg', 'image/jpg', 'image/png'];
    const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        alert('Please upload a PDF, DOC, DOCX, TXT, JPG, or PNG file');
        return;
    }

    // Add to uploaded files
    const fileData = {
        id: Date.now(),
        name: file.name,
        type: file.type,
        size: file.size,
        file: file
    };

    appState.uploadedFiles.push(fileData);
    displayUploadedFiles();

    // Notify user
    addChatMessage('assistant', `I've received your file: ${file.name}. You can now ask me questions about it or request a quiz from it.`);
}

function displayUploadedFiles() {
    const container = document.getElementById('uploadedFiles');
    container.innerHTML = '';

    appState.uploadedFiles.forEach(fileData => {
        const item = document.createElement('div');
        item.className = 'uploaded-file-item';
        item.innerHTML = `
            <span class="file-icon">📄</span>
            <span class="file-name">${fileData.name}</span>
            <button class="file-remove" onclick="removeFile(${fileData.id})" title="Remove file">×</button>
        `;
        container.appendChild(item);
    });
}

function removeFile(fileId) {
    appState.uploadedFiles = appState.uploadedFiles.filter(f => f.id !== fileId);
    displayUploadedFiles();
}

function toggleVoiceInput() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
        return;
    }

    if (appState.isVoiceRecording) {
        stopVoiceInput();
    } else {
        startVoiceInput();
    }
}

function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    appState.recognition = new SpeechRecognition();
    appState.recognition.continuous = false;
    appState.recognition.interimResults = false;
    appState.recognition.lang = 'en-US';

    appState.recognition.onstart = () => {
        appState.isVoiceRecording = true;
        document.getElementById('voiceButton').classList.add('active');
        document.getElementById('voiceStatus').classList.remove('hidden');
    };

    appState.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('chatInput').value = transcript;
    };

    appState.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopVoiceInput();
        alert('Voice recognition error. Please try again.');
    };

    appState.recognition.onend = () => {
        stopVoiceInput();
    };

    appState.recognition.start();
}

function stopVoiceInput() {
    if (appState.recognition) {
        appState.recognition.stop();
    }
    appState.isVoiceRecording = false;
    document.getElementById('voiceButton').classList.remove('active');
    document.getElementById('voiceStatus').classList.add('hidden');
}

function addChatMessage(role, content, messageId = null) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (messageId) {
        messageDiv.id = messageId;
    }

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = `<p>${content}</p>`;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    messagesDiv.appendChild(messageDiv);

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Add to history (only for non-loading messages)
    if (!messageId || !messageId.startsWith('loading-')) {
        addToHistory(role, content);
    }
}

function removeChatMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    if (messageElement) {
        messageElement.remove();
    }
}

function generateAIResponse(userMessage, hasFileReference) {
    // Check if user wants to generate quiz from document
    const lowerMessage = userMessage.toLowerCase();
    const wantsQuiz = lowerMessage.includes('quiz') || lowerMessage.includes('generate');
    const mentionsTopic = lowerMessage.match(/topic\s+(\d+)|(\d+)(?:st|nd|rd|th)\s+topic/i);
    
    if (hasFileReference && wantsQuiz) {
        let topicNumber = null;
        if (mentionsTopic) {
            topicNumber = parseInt(mentionsTopic[1] || mentionsTopic[2]);
        }
        
        if (topicNumber) {
            return `I'll generate a quiz from the ${topicNumber}${getOrdinalSuffix(topicNumber)} topic in your uploaded document. This will be processed by the backend to extract content and create questions. (Backend integration pending)`;
        } else {
            return `I'll generate a quiz from your uploaded document. Please specify which topic or section you'd like the quiz to cover. (Backend integration pending)`;
        }
    }
    
    // Simple response generation (will be replaced with LLM API)
    const responses = [
        "That's a great question! Let me help you understand that concept better.",
        "I'd be happy to explain that. Here's what you need to know...",
        "Excellent question! This is an important concept in your learning journey.",
        "Let me break that down for you in a way that's easy to understand."
    ];
    
    let response = responses[Math.floor(Math.random() * responses.length)];
    
    if (hasFileReference) {
        response += " I can see you've uploaded a document. I can help you understand its content or generate quizzes from it.";
    }
    
    return response + " (This will be connected to the backend LLM for intelligent responses)";
}

function getOrdinalSuffix(num) {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return 'st';
    if (j === 2 && k !== 12) return 'nd';
    if (j === 3 && k !== 13) return 'rd';
    return 'th';
}

// ============================================
// Utility Functions
// ============================================

function addToHistory(type, content) {
    appState.conversationHistory.push({
        type: type,
        content: content,
        timestamp: new Date().toISOString()
    });
}

// ============================================
// Initialize App
// ============================================

// ============================================
// Authentication Functions
// ============================================

let currentAuthMode = 'signin';

function switchAuthMode(mode) {
    currentAuthMode = mode;
    const signupFields = document.getElementById('signupFields');
    const authTitle = document.getElementById('authTitle');
    const authSubtitle = document.getElementById('authSubtitle');
    const authSubmitText = document.getElementById('authSubmitText');
    const authFooterText = document.getElementById('authFooterText');
    const authTabs = document.querySelectorAll('.auth-tab');

    if (!authTitle) return; // Section not loaded yet

    authTabs.forEach(tab => tab.classList.remove('active'));
    
    if (mode === 'signup') {
        signupFields.classList.remove('hidden');
        authTitle.textContent = 'Sign Up';
        authSubtitle.textContent = 'Create a new account to get started';
        authSubmitText.textContent = 'Sign Up';
        authFooterText.innerHTML = 'Already have an account? <a href="#" onclick="switchAuthMode(\'signin\'); return false;">Sign In</a>';
        authTabs[1].classList.add('active');
    } else {
        signupFields.classList.add('hidden');
        authTitle.textContent = 'Sign In';
        authSubtitle.textContent = 'Welcome back! Please sign in to your account.';
        authSubmitText.textContent = 'Sign In';
        authFooterText.innerHTML = 'Don\'t have an account? <a href="#" onclick="switchAuthMode(\'signup\'); return false;">Sign Up</a>';
        authTabs[0].classList.add('active');
    }
}

async function handleAuth(event) {
    event.preventDefault();
    
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    const submitBtn = document.querySelector('.auth-submit');
    const originalText = submitBtn.innerHTML;
    
    // Show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span>Processing...</span>';
    
    try {
    if (currentAuthMode === 'signup') {
        const name = document.getElementById('authName').value;
        const confirmPassword = document.getElementById('authConfirmPassword').value;
            
            if (!name || name.trim().length === 0) {
                alert('Please enter your name');
                return;
            }
        
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }
        
            if (password.length < 6) {
                alert('Password must be at least 6 characters long');
                return;
            }
            
            // Call backend API for sign-up
            const response = await fetch('http://localhost:5000/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name.trim(),
                    email: email.trim(),
                    password: password
                })
            });
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.error || errorMessage;
                } catch (jsonError) {
                    const text = await response.text();
                    errorMessage = text || errorMessage;
                }
                
                // Handle 404 specifically
                if (response.status === 404) {
                    errorMessage = `Endpoint not found (404). Please check:\n1. Backend server is running on http://localhost:5000\n2. Visit http://localhost:5000/docs to see available endpoints\n3. Restart the backend server if you just added this feature`;
                }
                
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Store authentication info
                appState.currentUser = {
                    user_id: data.user_id,
                    name: data.name,
                    email: data.email
                };
                appState.authToken = data.token;
                appState.isAuthenticated = true;
                
                // Store in localStorage
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('user', JSON.stringify(appState.currentUser));
                
                // Update UI
                updateAuthUI();
                
                alert('Account created successfully! Welcome!');
        document.getElementById('authForm').reset();
                showSection('home');
    } else {
                throw new Error(data.error || 'Failed to create account');
            }
        } else {
            // Sign in
            const response = await fetch('http://localhost:5000/api/auth/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email.trim(),
                    password: password
                })
            });
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.error || errorMessage;
                } catch (jsonError) {
                    const text = await response.text();
                    errorMessage = text || errorMessage;
                }
                
                // Handle 404 specifically
                if (response.status === 404) {
                    errorMessage = `Endpoint not found (404). Please check:\n1. Backend server is running on http://localhost:5000\n2. Visit http://localhost:5000/docs to see available endpoints\n3. Restart the backend server if you just added this feature`;
                }
                
                throw new Error(errorMessage);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Store authentication info
                appState.currentUser = {
                    user_id: data.user_id,
                    name: data.name,
                    email: data.email
                };
                appState.authToken = data.token;
                appState.isAuthenticated = true;
                
                // Store in localStorage
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('user', JSON.stringify(appState.currentUser));
                
                // Update UI
                updateAuthUI();
                
                alert('Signed in successfully!');
                document.getElementById('authForm').reset();
                showSection('home');
            } else {
                throw new Error(data.error || 'Failed to sign in');
            }
        }
    } catch (error) {
        console.error('Authentication error:', error);
        alert(error.message || 'An error occurred. Please try again.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// ============================================
// YouTube RAG Functions
// ============================================

let currentVideoId = null;

async function processYouTubeVideo() {
    // Check authentication
    if (!requireAuth('process YouTube videos')) {
        return;
    }
    
    const videoUrlInput = document.getElementById('youtubeVideoUrl');
    const processBtn = document.getElementById('processVideoBtn');
    const statusDiv = document.getElementById('videoProcessingStatus');
    const videoInfoDiv = document.getElementById('videoInfo');
    const qaSection = document.getElementById('qaSection');
    
    const videoUrl = videoUrlInput.value.trim();
    
    if (!videoUrl) {
        alert('Please enter a YouTube video URL or video ID');
        return;
    }
    
    // Disable button and show loading
    processBtn.disabled = true;
    processBtn.innerHTML = '<span>Processing...</span>';
    statusDiv.classList.remove('hidden');
    statusDiv.className = 'status-message status-loading';
    statusDiv.innerHTML = '<span class="spinner"></span> Processing video transcript...';
    videoInfoDiv.classList.add('hidden');
    
    try {
        const response = await fetch('http://localhost:5000/api/youtube/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                video_url: videoUrl
            })
        });
        
        // Check if response is ok
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
            try {
                const errorData = await response.json();
                // FastAPI returns errors in 'detail' field
                errorMessage = errorData.detail || errorData.error || errorMessage;
            } catch (jsonError) {
                // If response is not JSON, use status text
                const text = await response.text();
                errorMessage = text || errorMessage;
            }
            
            // Handle 404 specifically
            if (response.status === 404) {
                errorMessage = `Endpoint not found (404). The YouTube RAG feature may not be available. Please check:\n1. Backend server is running on http://localhost:5000\n2. Visit http://localhost:5000/docs to see available endpoints\n3. Restart the backend server if you just added this feature`;
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentVideoId = data.video_id;
            
            // Show success status
            statusDiv.className = 'status-message status-success';
            const successMsg = data.message || 'Video processed successfully!';
            statusDiv.innerHTML = `<span class="status-icon">✅</span> ${successMsg}`;
            
            // Show video info
            document.getElementById('currentVideoId').textContent = currentVideoId;
            if (data.transcript_length) {
                const details = document.querySelector('.video-details');
                if (details && !details.querySelector('.transcript-info')) {
                    const info = document.createElement('p');
                    info.className = 'transcript-info';
                    info.innerHTML = `<strong>Transcript Length:</strong> ${data.transcript_length.toLocaleString()} characters`;
                    details.appendChild(info);
                }
            }
            if (data.chunks_count) {
                const details = document.querySelector('.video-details');
                if (details) {
                    const chunksInfo = details.querySelector('.chunks-info');
                    if (!chunksInfo) {
                        const info = document.createElement('p');
                        info.className = 'chunks-info';
                        info.innerHTML = `<strong>Chunks Created:</strong> ${data.chunks_count}`;
                        details.appendChild(info);
                    }
                }
            }
            videoInfoDiv.classList.remove('hidden');
            
            // Show Q&A section
            qaSection.classList.remove('hidden');
            qaSection.style.display = 'block';
            
            // Clear previous answers
            document.getElementById('youtubeAnswers').innerHTML = '';
            
            // Clear input
            videoUrlInput.value = '';
        } else {
            throw new Error(data.error || 'Failed to process video');
        }
    } catch (error) {
        console.error('Error processing video:', error);
        console.error('Full error object:', error);
        statusDiv.className = 'status-message status-error';
        
        // Provide more helpful error messages
        let errorMessage = error.message || 'Failed to process video.';
        
        // Handle network errors
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = 'Cannot connect to server. Make sure the backend is running on http://localhost:5000';
        } else if (errorMessage.includes('captions') || errorMessage.includes('transcript') || errorMessage.includes('No captions')) {
            errorMessage += ' Make sure the video has English captions enabled.';
        } else if (errorMessage.includes('Embeddings') || errorMessage.includes('sentence-transformers')) {
            errorMessage += ' Please install: pip install sentence-transformers';
        } else if (errorMessage.includes('LLM') || errorMessage.includes('GEMINI_API_KEY') || errorMessage.includes('API key')) {
            errorMessage += ' Please set GEMINI_API_KEY in your .env file. Get your key from: https://makersuite.google.com/app/apikey';
        } else if (errorMessage.includes('Invalid YouTube URL') || errorMessage.includes('video ID')) {
            errorMessage += ' Please provide a valid YouTube video URL or video ID.';
        }
        
        statusDiv.innerHTML = `<span class="status-icon">❌</span> Error: ${errorMessage}`;
        videoInfoDiv.classList.add('hidden');
        qaSection.classList.add('hidden');
        qaSection.style.display = 'none';
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = '<span>Process Video</span>';
    }
}

async function askYouTubeQuestion() {
    // Check authentication
    if (!requireAuth('ask questions about videos')) {
        return;
    }
    
    const questionInput = document.getElementById('youtubeQuestion');
    const askBtn = document.getElementById('askQuestionBtn');
    const answersContainer = document.getElementById('youtubeAnswers');
    
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    if (!currentVideoId) {
        alert('Please process a video first');
        return;
    }
    
    // Disable button and show loading
    askBtn.disabled = true;
    askBtn.innerHTML = '<span>Asking...</span>';
    
    // Add question to UI
    const questionDiv = document.createElement('div');
    questionDiv.className = 'answer-item question-item';
    questionDiv.innerHTML = `
        <div class="answer-header">
            <span class="answer-label">Question:</span>
            <span class="answer-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="answer-content">${question}</div>
    `;
    answersContainer.appendChild(questionDiv);
    
    // Add loading answer
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'answer-item loading-item';
    loadingDiv.id = 'loadingAnswer';
    loadingDiv.innerHTML = `
        <div class="answer-header">
            <span class="answer-label">Answer:</span>
            <span class="spinner-small"></span>
        </div>
        <div class="answer-content">Thinking...</div>
    `;
    answersContainer.appendChild(loadingDiv);
    
    // Scroll to bottom
    answersContainer.scrollTop = answersContainer.scrollHeight;
    
    try {
        const response = await fetch('http://localhost:5000/api/youtube/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                video_id: currentVideoId,
                question: question
            })
        });
        
        // Check if response is ok
        if (!response.ok) {
            const errorData = await response.json();
            // FastAPI returns errors in 'detail' field
            const errorMessage = errorData.detail || errorData.error || `HTTP ${response.status}: ${response.statusText}`;
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        // Remove loading
        const loadingElement = document.getElementById('loadingAnswer');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        if (data.success) {
            // Add answer to UI
            const answerDiv = document.createElement('div');
            answerDiv.className = 'answer-item answer-item-response';
            answerDiv.innerHTML = `
                <div class="answer-header">
                    <span class="answer-label">Answer:</span>
                    <span class="answer-time">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="answer-content">${data.answer}</div>
            `;
            answersContainer.appendChild(answerDiv);
        } else {
            throw new Error(data.error || 'Failed to get answer');
        }
    } catch (error) {
        console.error('Error asking question:', error);
        
        // Remove loading
        const loadingElement = document.getElementById('loadingAnswer');
        if (loadingElement) {
            loadingElement.remove();
        }
        
        // Show error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'answer-item error-item';
        errorDiv.innerHTML = `
            <div class="answer-header">
                <span class="answer-label">Error:</span>
            </div>
            <div class="answer-content">${error.message || 'Failed to get answer. Please try again.'}</div>
        `;
        answersContainer.appendChild(errorDiv);
    } finally {
        askBtn.disabled = false;
        askBtn.innerHTML = '<span>Ask Question</span>';
        questionInput.value = '';
        
        // Scroll to bottom
        answersContainer.scrollTop = answersContainer.scrollHeight;
    }
}

// Allow Enter key to submit question
document.addEventListener('DOMContentLoaded', () => {
    const questionInput = document.getElementById('youtubeQuestion');
    if (questionInput) {
        questionInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                askYouTubeQuestion();
            }
        });
    }
});

// ============================================
// Feedback Functions
// ============================================

function submitFeedback(event) {
    event.preventDefault();
    
    const feedbackData = {
        name: document.getElementById('feedbackName').value,
        email: document.getElementById('feedbackEmail').value,
        type: document.getElementById('feedbackType').value,
        subject: document.getElementById('feedbackSubject').value,
        message: document.getElementById('feedbackMessage').value,
        rating: document.querySelector('input[name="rating"]:checked')?.value || '0',
        timestamp: new Date().toISOString()
    };
    
    // Store feedback (will be replaced with backend API)
    const feedbacks = JSON.parse(localStorage.getItem('feedbacks') || '[]');
    feedbacks.push(feedbackData);
    localStorage.setItem('feedbacks', JSON.stringify(feedbacks));
    
    alert('Thank you for your feedback! We appreciate your input.');
    document.getElementById('feedbackForm').reset();
}

// Check authentication on page load (restore session if exists)
function checkAuthentication() {
    const authToken = localStorage.getItem('authToken');
    const userStr = localStorage.getItem('user');
    
    if (authToken && userStr) {
        try {
            const user = JSON.parse(userStr);
            appState.currentUser = user;
            appState.authToken = authToken;
            appState.isAuthenticated = true;
            
            // Update UI
            updateAuthUI();
            
            console.log('User authenticated:', user.name);
            return true;
        } catch (e) {
            console.error('Error parsing user data:', e);
            // Clear invalid data
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            return false;
        }
    }
    return false;
}

// Require authentication before performing an action
function requireAuth(actionName = 'this action') {
    if (!appState.isAuthenticated) {
        alert(`Please sign in to ${actionName}.`);
        showSection('auth');
        return false;
    }
    return true;
}

// Toggle user dropdown menu
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Close user dropdown when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.getElementById('userMenu');
    const userNameDisplay = document.getElementById('userNameDisplay');
    const dropdown = document.getElementById('userDropdown');
    
    if (userMenu && dropdown && !userMenu.contains(event.target)) {
        dropdown.classList.add('hidden');
    }
});

// Update authentication UI
function updateAuthUI() {
    const authLink = document.getElementById('authLink');
    const userMenu = document.getElementById('userMenu');
    const userNameDisplay = document.getElementById('userNameDisplay');
    const dropdown = document.getElementById('userDropdown');
    
    if (appState.isAuthenticated && appState.currentUser) {
        // Show user menu, hide sign in link
        if (authLink) {
            authLink.classList.add('hidden');
        }
        if (userMenu) {
            userMenu.classList.remove('hidden');
        }
        if (userNameDisplay) {
            userNameDisplay.textContent = appState.currentUser.name || 'User';
        }
        // Close dropdown when updating UI
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
    } else {
        // Show sign in link, hide user menu
        if (authLink) {
            authLink.classList.remove('hidden');
            authLink.textContent = 'Sign In';
        }
        if (userMenu) {
            userMenu.classList.add('hidden');
        }
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
    }
}

// Sign out function
function signOut() {
    appState.currentUser = null;
    appState.authToken = null;
    appState.isAuthenticated = false;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    
    // Update UI
    updateAuthUI();
    
    // Redirect to auth page
    showSection('auth');
}

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    
    // Check authentication (restore session if exists, but don't force redirect)
    checkAuthentication();
    
    // Show home page by default (users can browse freely)
    showSection('home');
    
    // Initialize canvas size for performance chart
    const canvas = document.getElementById('performanceChart');
    if (canvas) {
        // Set canvas dimensions
        const container = canvas.parentElement;
        canvas.width = container ? container.offsetWidth : 800;
        canvas.height = 300;
        
        // Initialize charts
        updatePerformanceChart();
        updateDifficultyChart();
    }
    
    console.log('AI Teacher Agent Frontend Initialized');
});

// Handle window resize
window.addEventListener('resize', () => {
    const canvas = document.getElementById('performanceChart');
    if (canvas) {
        canvas.width = canvas.offsetWidth;
        canvas.height = 300;
        updatePerformanceChart();
    }
});



