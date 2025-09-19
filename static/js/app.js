// AI Research Paper Generator - Frontend JavaScript

class PaperGenerator {
    constructor() {
        this.currentPaperId = null;
        this.currentPaper = null;
        this.currentFiles = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupSampleTopics();
    }

    bindEvents() {
        // Form submission
        document.getElementById('paperForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generatePaper();
        });

        // Plagiarism check
        document.getElementById('plagiarismBtn').addEventListener('click', () => {
            this.checkPlagiarism();
        });

        // PDF download
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadPDF();
            });
        }

        // LaTeX download
        const latexBtn = document.getElementById('latexBtn');
        if (latexBtn) {
            latexBtn.addEventListener('click', () => {
                this.downloadLaTeX();
            });
        }

        // Complete package download
        const packageBtn = document.getElementById('packageBtn');
        if (packageBtn) {
            packageBtn.addEventListener('click', () => {
                this.downloadCompletePackage();
            });
        }
        


        // Share button
        const shareBtn = document.getElementById('shareBtn');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => {
                this.sharePaper();
            });
        }

        // Copy link button
        const copyBtn = document.getElementById('copyLinkBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                this.copyShareLink();
            });
        }
    }

    setupSampleTopics() {
        document.querySelectorAll('.sample-topic').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const topic = e.target.getAttribute('data-topic');
                document.getElementById('topic').value = topic;
                
                // Add visual feedback
                e.target.classList.add('btn-primary');
                e.target.classList.remove('btn-outline-primary');
                setTimeout(() => {
                    e.target.classList.remove('btn-primary');
                    e.target.classList.add('btn-outline-primary');
                }, 1000);
            });
        });
    }

    async generatePaper() {
        const formData = this.getFormData();
        
        if (!formData.topic.trim()) {
            this.showAlert('Please enter a research topic', 'warning');
            return;
        }

        this.showLoading('Generating your research paper...');
        
        try {
            const response = await fetch('/api/paper/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                this.currentPaperId = data.paper_id;
                this.currentPaper = data.paper;
                this.displayPaper(data.paper);
                this.showAlert('Research paper generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to generate paper');
            }
        } catch (error) {
            console.error('Error generating paper:', error);
            this.showAlert(`Error: ${error.message}`, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    getFormData() {
        const sections = [];
        document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
            sections.push(checkbox.id);
        });

        const keywords = document.getElementById('keywords').value
            .split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0);

        return {
            topic: document.getElementById('topic').value.trim(),
            keywords: keywords,
            citation_style: document.getElementById('citationStyle').value,
            research_level: document.getElementById('researchLevel').value,
            research_field: document.getElementById('researchField').value,
            sections: sections
        };
    }

    displayPaper(paper) {
        const container = document.getElementById('paperContent');
        let html = '';

        // Title
        if (paper.title) {
            html += `<div class="paper-title">${this.escapeHtml(paper.title)}</div>`;
        }

        // Abstract
        if (paper.abstract) {
            html += this.createSection('Abstract', paper.abstract);
        }

        // Introduction
        if (paper.introduction) {
            html += this.createSection('1. Introduction', paper.introduction);
        }

        // Literature Review
        if (paper.literature_review) {
            html += this.createSection('2. Literature Review', paper.literature_review);
        }

        // Methodology
        if (paper.methodology) {
            html += this.createSection('3. Methodology', paper.methodology);
        }

        // Results
        if (paper.results) {
            html += this.createSection('4. Results', paper.results);
        }

        // Conclusion
        if (paper.conclusion) {
            html += this.createSection('5. Conclusion', paper.conclusion);
        }

        // Summary
        if (paper.summary && paper.summary.length > 0) {
            html += this.createSummarySection(paper.summary);
        }

        // References
        if (paper.references && paper.references.length > 0) {
            html += this.createReferencesSection(paper.references);
        }

        container.innerHTML = html;
        document.getElementById('resultsSection').style.display = 'block';
        
        // Show download buttons
        const downloadBtn = document.getElementById('downloadBtn');
        const latexBtn = document.getElementById('latexBtn');
        const packageBtn = document.getElementById('packageBtn');
        
        if (downloadBtn) {
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = () => this.downloadPDF();
        }
        if (latexBtn) {
            latexBtn.style.display = 'inline-block';
            latexBtn.onclick = () => this.downloadLaTeX();
        }
        if (packageBtn) {
            packageBtn.style.display = 'inline-block';
            packageBtn.onclick = () => this.downloadCompletePackage();
        }
        
        // Show real papers if available
        if (paper.real_papers && paper.real_papers.length > 0) {
            this.displayRealPapers(paper.real_papers);
        }
        
        // Show research domain if available
        if (paper.metadata && paper.metadata.research_domain) {
            this.displayResearchDomain(paper.metadata.research_domain, paper.metadata.domain_confidence);
        }
        
        // Show charts and images if available
        if (paper.charts && paper.charts.length > 0) {
            this.displayCharts(paper.charts);
        }
        
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
    }

    createSection(title, content) {
        return `
            <div class="paper-section fade-in">
                <h3 class="section-title">${this.escapeHtml(title)}</h3>
                <div class="section-content">${this.escapeHtml(content)}</div>
            </div>
        `;
    }

    createSummarySection(summaryPoints) {
        let html = `
            <div class="paper-section fade-in">
                <h3 class="section-title">Key Insights</h3>
                <div class="summary-points">
        `;
        
        summaryPoints.forEach(point => {
            html += `
                <div class="summary-point">
                    <i class="fas fa-lightbulb"></i>
                    <span>${this.escapeHtml(point)}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }

    createReferencesSection(references) {
        let html = `
            <div class="paper-section fade-in">
                <h3 class="section-title">References</h3>
                <div class="references-list">
        `;
        
        references.forEach((ref, index) => {
            html += `
                <div class="reference-item">
                    <strong>[${index + 1}]</strong> ${this.escapeHtml(ref)}
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }

    async checkPlagiarism() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to check', 'warning');
            return;
        }

        this.showAlert('Checking for plagiarism...', 'info');

        try {
            const response = await fetch(`/api/plagiarism/check-paper/${this.currentPaperId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.displayPlagiarismResults(data.plagiarism_check);
            } else {
                throw new Error(data.error || 'Plagiarism check failed');
            }
        } catch (error) {
            console.error('Error checking plagiarism:', error);
            this.showAlert(`Plagiarism check error: ${error.message}`, 'danger');
        }
    }

    displayQualityResults(report) {
        const container = document.getElementById('qualityContent');
        
        let gradeColor = 'success';
        if (report.grade === 'C' || report.grade === 'D') gradeColor = 'warning';
        else if (report.grade === 'F') gradeColor = 'danger';

        let html = `
            <div class="row mb-4">
                <div class="col-md-3 text-center">
                    <div class="display-4 text-${gradeColor}">${report.grade}</div>
                    <div class="text-muted">Overall Grade</div>
                </div>
                <div class="col-md-9">
                    <h6>Quality Metrics</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-2">
                                <small>Citation Quality</small>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${report.metrics.citation_quality}%">${report.metrics.citation_quality}%</div>
                                </div>
                            </div>
                            <div class="mb-2">
                                <small>Structure Score</small>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${report.metrics.structure_score}%">${report.metrics.structure_score}%</div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-2">
                                <small>Originality Index</small>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${report.metrics.originality_index}%">${report.metrics.originality_index}%</div>
                                </div>
                            </div>
                            <div class="mb-2">
                                <small>Academic Tone</small>
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${report.metrics.academic_tone_score}%">${report.metrics.academic_tone_score}%</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-thumbs-up text-success me-2"></i>Strengths</h6>
                    <ul class="list-unstyled">
        `;
        
        report.strengths.forEach(strength => {
            html += `<li><i class="fas fa-check text-success me-2"></i>${strength}</li>`;
        });
        
        html += `
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-exclamation-triangle text-warning me-2"></i>Recommendations</h6>
                    <ul class="list-unstyled">
        `;
        
        report.recommendations.forEach(rec => {
            html += `<li><i class="fas fa-arrow-right text-warning me-2"></i>${rec}</li>`;
        });
        
        html += `
                    </ul>
                </div>
            </div>
        `;

        container.innerHTML = html;
        document.getElementById('qualityResults').style.display = 'block';
        document.getElementById('qualityResults').scrollIntoView({ behavior: 'smooth' });
    }

    displayPeerReviewResults(review) {
        const container = document.getElementById('peerReviewContent');
        
        let scoreColor = 'success';
        if (review.overall_score < 70) scoreColor = 'warning';
        if (review.overall_score < 60) scoreColor = 'danger';

        let html = `
            <div class="row mb-4">
                <div class="col-md-3 text-center">
                    <div class="display-4 text-${scoreColor}">${review.overall_score}</div>
                    <div class="text-muted">Overall Score</div>
                </div>
                <div class="col-md-9">
                    <h6>Detailed Scores</h6>
                    <div class="row">
        `;
        
        Object.entries(review.detailed_scores).forEach(([key, value]) => {
            const label = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `
                <div class="col-md-6 mb-2">
                    <small>${label}</small>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${value}%">${value}%</div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-4">
                    <h6><i class="fas fa-star text-success me-2"></i>Strengths</h6>
                    <ul class="list-unstyled">
        `;
        
        review.strengths.forEach(strength => {
            html += `<li><i class="fas fa-plus text-success me-2"></i>${strength}</li>`;
        });
        
        html += `
                    </ul>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-minus text-warning me-2"></i>Weaknesses</h6>
                    <ul class="list-unstyled">
        `;
        
        review.weaknesses.forEach(weakness => {
            html += `<li><i class="fas fa-minus text-warning me-2"></i>${weakness}</li>`;
        });
        
        html += `
                    </ul>
                </div>
                <div class="col-md-4">
                    <h6><i class="fas fa-lightbulb text-info me-2"></i>Suggestions</h6>
                    <ul class="list-unstyled">
        `;
        
        review.suggestions.forEach(suggestion => {
            html += `<li><i class="fas fa-arrow-right text-info me-2"></i>${suggestion}</li>`;
        });
        
        html += `
                    </ul>
                </div>
            </div>
            
            <div class="mt-3">
                <h6><i class="fas fa-comment text-primary me-2"></i>Reviewer Comments</h6>
        `;
        
        review.reviewer_comments.forEach(comment => {
            html += `<p class="text-muted"><em>"${comment}"</em></p>`;
        });
        
        html += `</div>`;

        container.innerHTML = html;
        document.getElementById('peerReviewResults').style.display = 'block';
        document.getElementById('peerReviewResults').scrollIntoView({ behavior: 'smooth' });
    }

    displayPlagiarismResults(results) {
        const container = document.getElementById('plagiarismContent');
        
        let statusClass = 'plagiarism-low';
        if (results.plagiarism_score >= 20) statusClass = 'plagiarism-high';
        else if (results.plagiarism_score >= 10) statusClass = 'plagiarism-medium';

        let html = `
            <div class="plagiarism-score ${statusClass}">
                <i class="fas fa-shield-alt me-2"></i>
                Plagiarism Score: ${results.plagiarism_score}%
                <br>
                <small>Status: ${results.status}</small>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-info-circle me-2"></i>Document Statistics</h6>
                    <ul class="list-unstyled">
                        <li><strong>Word Count:</strong> ${results.word_count}</li>
                        <li><strong>Character Count:</strong> ${results.char_count}</li>
                        <li><strong>Checked At:</strong> ${results.checked_at}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-chart-bar me-2"></i>Risk Assessment</h6>
                    <div class="progress mb-2">
                        <div class="progress-bar bg-${results.color}" role="progressbar" 
                             style="width: ${results.plagiarism_score}%" 
                             aria-valuenow="${results.plagiarism_score}" 
                             aria-valuemin="0" aria-valuemax="100">
                            ${results.plagiarism_score}%
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (results.sources && results.sources.length > 0) {
            html += `
                <div class="plagiarism-sources">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Similar Sources Found</h6>
            `;
            
            results.sources.forEach(source => {
                html += `
                    <div class="source-item">
                        <strong>Similarity: ${source.similarity}</strong><br>
                        <a href="${source.url}" target="_blank" class="text-decoration-none">
                            ${this.escapeHtml(source.title)}
                        </a>
                    </div>
                `;
            });
            
            html += `</div>`;
        }

        container.innerHTML = html;
        document.getElementById('plagiarismResults').style.display = 'block';
        document.getElementById('plagiarismResults').scrollIntoView({ behavior: 'smooth' });
    }

    async performQualityCheck() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to analyze', 'warning');
            return;
        }

        this.showAlert('Analyzing paper quality...', 'info');

        try {
            const response = await fetch(`/api/assistant/quality-check/${this.currentPaperId}`);
            const data = await response.json();

            if (data.success) {
                this.displayQualityResults(data.quality_report);
            } else {
                throw new Error(data.error || 'Quality check failed');
            }
        } catch (error) {
            console.error('Error in quality check:', error);
            this.showAlert(`Quality check error: ${error.message}`, 'danger');
        }
    }

    async performPeerReview() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to review', 'warning');
            return;
        }

        this.showAlert('Performing AI peer review...', 'info');

        try {
            const response = await fetch(`/api/assistant/peer-review/${this.currentPaperId}`, {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                this.displayPeerReviewResults(data.peer_review);
            } else {
                throw new Error(data.error || 'Peer review failed');
            }
        } catch (error) {
            console.error('Error in peer review:', error);
            this.showAlert(`Peer review error: ${error.message}`, 'danger');
        }
    }

    async downloadPDF() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to download', 'warning');
            return;
        }

        this.showAlert('Generating PDF...', 'info');

        try {
            const response = await fetch(`/api/pdf/export/${this.currentPaperId}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `research_paper_${new Date().getTime()}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert('PDF downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to generate PDF');
            }
        } catch (error) {
            console.error('Error downloading PDF:', error);
            this.showAlert(`PDF download error: ${error.message}`, 'danger');
        }
    }

    async downloadLaTeX() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to download', 'warning');
            return;
        }

        this.showAlert('Generating LaTeX...', 'info');

        try {
            const response = await fetch(`/api/pdf/latex/${this.currentPaperId}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `research_paper_${new Date().getTime()}.tex`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert('LaTeX file downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to generate LaTeX');
            }
        } catch (error) {
            console.error('Error downloading LaTeX:', error);
            this.showAlert(`LaTeX download error: ${error.message}`, 'danger');
        }
    }

    async downloadCompletePackage() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to download', 'warning');
            return;
        }

        this.showAlert('Generating complete research package...', 'info');

        try {
            const response = await fetch(`/api/pdf/download-files/${this.currentPaperId}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `research_package_${new Date().getTime()}.zip`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert('Complete research package downloaded!', 'success');
            } else {
                throw new Error('Failed to generate package');
            }
        } catch (error) {
            console.error('Error downloading package:', error);
            this.showAlert(`Package download error: ${error.message}`, 'danger');
        }
    }

    displayRealPapers(papers) {
        const container = document.getElementById('paperContent');
        let html = `
            <div class="paper-section fade-in mt-4">
                <h3 class="section-title"><i class="fas fa-search me-2"></i>Real Academic Papers Found</h3>
                <div class="alert alert-info">
                    <i class="fas fa-lightbulb me-2"></i>
                    These are real academic papers found using AI search that relate to your topic.
                </div>
        `;
        
        papers.forEach((paper, index) => {
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <h6 class="card-title">${this.escapeHtml(paper.title)}</h6>
                        <p class="card-text">
                            <strong>Authors:</strong> ${this.escapeHtml(paper.authors)}<br>
                            <strong>Journal:</strong> ${this.escapeHtml(paper.journal)} (${paper.year})<br>
                            ${paper.doi ? `<strong>DOI:</strong> ${this.escapeHtml(paper.doi)}<br>` : ''}
                            <strong>Abstract:</strong> ${this.escapeHtml(paper.abstract)}
                        </p>
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
        container.innerHTML += html;
    }
    
    displayResearchDomain(domain, confidence) {
        const container = document.getElementById('paperContent');
        let confidenceColor = 'success';
        if (confidence === 'medium') confidenceColor = 'warning';
        if (confidence === 'low') confidenceColor = 'secondary';
        
        let html = `
            <div class="paper-section fade-in mt-3">
                <div class="alert alert-info">
                    <h6 class="mb-2">
                        <i class="fas fa-tag me-2"></i>
                        Academic Domain Classification
                    </h6>
                    <div class="mb-2">
                        <code class="fs-5 text-primary">[Domain: ${this.escapeHtml(domain)}]</code>
                    </div>
                    <div class="d-flex align-items-center">
                        <small class="text-muted me-3">
                            Classification Style: IEEE/Springer/APA/MLA Standard
                        </small>
                        <small class="text-muted">
                            Confidence: <span class="badge bg-${confidenceColor}">${confidence}</span>
                        </small>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML += html;
    }
    
    displayAdditionalFiles(files) {
        const container = document.getElementById('paperContent');
        let html = `
            <div class="paper-section fade-in mt-4">
                <h3 class="section-title"><i class="fas fa-folder me-2"></i>Generated Files</h3>
                <div class="row">
        `;
        
        const fileTypes = [
            { key: 'bibliography', name: 'Bibliography', icon: 'fas fa-book', desc: 'Reference list in citation style' },
            { key: 'research_notes', name: 'Research Notes', icon: 'fas fa-sticky-note', desc: 'Key papers and research questions' },
            { key: 'abstract_only', name: 'Abstract Only', icon: 'fas fa-file-alt', desc: 'Just the abstract text' },
            { key: 'citations_list', name: 'Citations List', icon: 'fas fa-quote-right', desc: 'Formatted citations' }
        ];
        
        fileTypes.forEach(fileType => {
            if (files[fileType.key]) {
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card file-card" onclick="paperGenerator.showFileContent('${fileType.key}', '${fileType.name}')" style="cursor: pointer;">
                            <div class="card-body text-center">
                                <i class="${fileType.icon} fa-2x text-primary mb-2"></i>
                                <h6 class="card-title">${fileType.name}</h6>
                                <p class="card-text small text-muted">${fileType.desc}</p>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        html += `
                </div>
            </div>
        `;
        
        container.innerHTML += html;
        
        // Store files for later access
        this.currentFiles = files;
    }
    
    showFileContent(fileKey, fileName) {
        if (!this.currentFiles || !this.currentFiles[fileKey]) {
            this.showAlert('File content not available', 'warning');
            return;
        }
        
        const content = this.currentFiles[fileKey];
        const modalHtml = `
            <div class="modal fade" id="fileModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-file-alt me-2"></i>
                                ${fileName}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <pre class="file-content">${this.escapeHtml(Array.isArray(content) ? content.join('\n\n') : content)}</pre>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="paperGenerator.downloadFileContent('${fileKey}', '${fileName}')">
                                <i class="fas fa-download me-1"></i>Download
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal
        const existingModal = document.getElementById('fileModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('fileModal'));
        modal.show();
    }
    
    downloadFileContent(fileKey, fileName) {
        if (!this.currentFiles || !this.currentFiles[fileKey]) {
            this.showAlert('File content not available', 'warning');
            return;
        }
        
        const content = this.currentFiles[fileKey];
        const fileContent = Array.isArray(content) ? content.join('\n\n') : content;
        const extension = fileKey.includes('bibliography') || fileKey.includes('notes') ? '.md' : '.txt';
        const filename = `${fileName.toLowerCase().replace(/\s+/g, '_')}${extension}`;
        
        this.downloadText(fileContent, filename);
        this.showAlert(`${fileName} downloaded successfully!`, 'success');
    }
    
    displayCharts(charts) {
        const container = document.getElementById('paperContent');
        let html = `
            <div class="paper-section fade-in mt-4">
                <h3 class="section-title"><i class="fas fa-chart-bar me-2"></i>Research Visualizations</h3>
                <div class="row">
        `;
        
        charts.forEach((chart, index) => {
            html += `
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <img src="${chart.image}" class="card-img-top" alt="${chart.title}" style="height: 300px; object-fit: contain;">
                        <div class="card-body">
                            <h6 class="card-title">${this.escapeHtml(chart.title)}</h6>
                            <p class="card-text small text-muted">${this.escapeHtml(chart.caption)}</p>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        container.innerHTML += html;
    }
    
    async importPdfFromUrl() {
        const pdfUrl = document.getElementById('pdfUrl').value.trim();
        
        if (!pdfUrl) {
            this.showAlert('Please enter a PDF URL', 'warning');
            return;
        }
        
        this.showAlert('Importing PDF from URL...', 'info');
        
        try {
            const response = await fetch('/api/import/import-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pdf_url: pdfUrl })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentPaperId = data.paper_id;
                this.currentPaper = data.paper;
                this.displayPaper(data.paper);
                this.showAlert('PDF imported successfully!', 'success');
                document.getElementById('pdfUrl').value = '';
            } else {
                throw new Error(data.error || 'Import failed');
            }
        } catch (error) {
            console.error('PDF import error:', error);
            this.showAlert(`Import error: ${error.message}`, 'danger');
        }
    }
    
    async importPdfFromFile() {
        const fileInput = document.getElementById('pdfFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showAlert('Please select a PDF file', 'warning');
            return;
        }
        
        this.showAlert('Processing PDF file...', 'info');
        
        try {
            const formData = new FormData();
            formData.append('pdf_file', file);
            
            const response = await fetch('/api/import/import-file', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentPaperId = data.paper_id;
                this.currentPaper = data.paper;
                this.displayPaper(data.paper);
                this.showAlert('PDF file imported successfully!', 'success');
                fileInput.value = '';
            } else {
                throw new Error(data.error || 'Import failed');
            }
        } catch (error) {
            console.error('PDF file import error:', error);
            this.showAlert(`Import error: ${error.message}`, 'danger');
        }
    }

    async sharePaper() {
        if (!this.currentPaperId) {
            this.showAlert('No paper to share', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/collaboration/share/${this.currentPaperId}`, {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                const shareUrl = `${window.location.origin}${data.share_url}`;
                document.getElementById('shareLink').value = shareUrl;
                
                const modal = new bootstrap.Modal(document.getElementById('shareModal'));
                modal.show();
            } else {
                throw new Error(data.error || 'Failed to create share link');
            }
        } catch (error) {
            console.error('Share error:', error);
            this.showAlert(`Share error: ${error.message}`, 'danger');
        }
    }

    copyShareLink() {
        const shareLink = document.getElementById('shareLink');
        shareLink.select();
        document.execCommand('copy');
        this.showAlert('Share link copied to clipboard!', 'success');
    }

    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    downloadText(content, filename) {
        const blob = new Blob([content], { type: 'text/plain' });
        this.downloadBlob(blob, filename);
    }

    showLoading(message) {
        document.getElementById('loadingText').textContent = message;
        document.getElementById('loadingIndicator').style.display = 'block';
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    }

    hideLoading() {
        document.getElementById('loadingIndicator').style.display = 'none';
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('generateBtn').innerHTML = '<i class="fas fa-magic me-2"></i>Generate Research Paper';
    }

    showAlert(message, type) {
        // Remove existing alerts
        document.querySelectorAll('.alert').forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.paperGenerator = new PaperGenerator();
});