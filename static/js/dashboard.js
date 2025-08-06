/**
 * Affinity Reporting Status Dashboard
 * Real-time display of medical imaging case status with Radcon levels
 */

class AffinityDashboard {
    constructor() {
        this.config = null;
        this.initializeElements();
        this.loadConfiguration();
        this.loadCaseData();
        this.setupAutoRefresh();
    }

    initializeElements() {
        // Display elements for case counts
        this.displayMriCases = document.getElementById('displayMriCases');
        this.displayCtCases = document.getElementById('displayCtCases');
        this.displayXrayCases = document.getElementById('displayXrayCases');
        this.displayNucmedCases = document.getElementById('displayNucmedCases');
        this.displayUltrasoundCases = document.getElementById('displayUltrasoundCases');
        this.lastUpdated = document.getElementById('lastUpdated');
        this.totalCasesHeader = document.getElementById('totalCasesHeader');

        // Status display elements
        this.statusLevel = document.getElementById('statusLevel');
        this.statusDescription = document.getElementById('statusDescription');
        this.statusCircle = document.querySelector('.status-circle');
        this.turnaroundTime = document.getElementById('turnaroundTime');
        this.turnaroundNote = document.getElementById('turnaroundNote');

        // Individual modality elements
        this.mriElements = {
            badge: document.getElementById('mriStatusBadge'),
            dot: document.getElementById('mriStatusDot'),
            count: document.getElementById('mriCaseCount'),
            turnaround: document.getElementById('mriTurnaround')
        };

        this.ctElements = {
            badge: document.getElementById('ctStatusBadge'),
            dot: document.getElementById('ctStatusDot'),
            count: document.getElementById('ctCaseCount'),
            turnaround: document.getElementById('ctTurnaround')
        };

        this.xrayElements = {
            badge: document.getElementById('xrayStatusBadge'),
            dot: document.getElementById('xrayStatusDot'),
            count: document.getElementById('xrayCaseCount'),
            turnaround: document.getElementById('xrayTurnaround')
        };

        this.nucmedElements = {
            badge: document.getElementById('nucmedStatusBadge'),
            dot: document.getElementById('nucmedStatusDot'),
            count: document.getElementById('nucmedCaseCount'),
            turnaround: document.getElementById('nucmedTurnaround')
        };

        this.ultrasoundElements = {
            badge: document.getElementById('ultrasoundStatusBadge'),
            dot: document.getElementById('ultrasoundStatusDot'),
            count: document.getElementById('ultrasoundCaseCount'),
            turnaround: document.getElementById('ultrasoundTurnaround')
        };

        // Summary elements
        this.totalCases = document.getElementById('totalCases');
        this.avgTurnaround = document.getElementById('avgTurnaround');
        this.workload = document.getElementById('workload');

    }

    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            this.config = await response.json();
        } catch (error) {
            console.error('Error loading configuration:', error);
            // Use default configuration if API fails
            this.config = {
                mri_radcon5_threshold: 40, mri_radcon3_threshold: 60, mri_radcon1_threshold: 90,
                ct_radcon5_threshold: 20, ct_radcon3_threshold: 35, ct_radcon1_threshold: 45,
                xray_radcon5_threshold: 20, xray_radcon3_threshold: 40, xray_radcon1_threshold: 55,
                nucmed_radcon5_threshold: 10, nucmed_radcon3_threshold: 15, nucmed_radcon1_threshold: 20,
                ultrasound_radcon5_threshold: 30, ultrasound_radcon3_threshold: 50, ultrasound_radcon1_threshold: 60,
                mri_processing_rate: 16, ct_processing_rate: 20, xray_processing_rate: 40, nucmed_processing_rate: 5, ultrasound_processing_rate: 40,
                radcon_4_threshold: 110, radcon_3_threshold: 175, radcon_2_threshold: 206
            };
        }
    }

    async loadCaseData() {
        try {
            const response = await fetch('/api/volumes');
            const data = await response.json();
            
            this.currentCases = {
                mri: data.mri || 0,
                ct: data.ct || 0,
                xray: data.xray || 0,
                nucmed: data.nucmed || 0,
                ultrasound: data.ultrasound || 0
            };
            
            // Store radiologist staffing level
            this.radiologistStaffing = data.radiologist_staffing || 100;
            
            this.updateLastUpdatedTime(data.timestamp, data.updated_by);
            this.updateDashboard();
            
        } catch (error) {
            console.error('Error loading case data:', error);
            this.showError('Unable to load current case data');
        }
    }

    setupAutoRefresh() {
        // Refresh data every 5 seconds for faster updates
        setInterval(() => {
            this.loadConfiguration(); // Reload config in case it changed
            this.loadCaseData();
        }, 5000);
    }

    updateLastUpdatedTime(timestamp, updatedBy) {
        if (timestamp && updatedBy) {
            const date = new Date(timestamp);
            const timeStr = date.toLocaleString();
            this.lastUpdated.textContent = `Last updated: ${timeStr} by ${updatedBy}`;
        } else {
            this.lastUpdated.textContent = 'Last updated: No data available';
        }
    }

    showError(message) {
        this.lastUpdated.textContent = `Error: ${message}`;
        this.lastUpdated.className = 'text-danger me-2';
    }

    getCaseValues() {
        return this.currentCases || { mri: 0, ct: 0, xray: 0, nucmed: 0, ultrasound: 0 };
    }

    calculateModalityStatus(cases, type) {
        if (!this.config) return { level: 'green', text: 'Normal', class: 'bg-success' };
        
        let thresholds;
        
        // Use dynamic thresholds from configuration (Radcon 5 = yellow, 3 = orange, 1 = red)
        switch(type) {
            case 'mri':
                thresholds = { yellow: this.config.mri_radcon5_threshold, orange: this.config.mri_radcon3_threshold, red: this.config.mri_radcon1_threshold };
                break;
            case 'ct':
                thresholds = { yellow: this.config.ct_radcon5_threshold, orange: this.config.ct_radcon3_threshold, red: this.config.ct_radcon1_threshold };
                break;
            case 'xray':
                thresholds = { yellow: this.config.xray_radcon5_threshold, orange: this.config.xray_radcon3_threshold, red: this.config.xray_radcon1_threshold };
                break;
            case 'nucmed':
                thresholds = { yellow: this.config.nucmed_radcon5_threshold, orange: this.config.nucmed_radcon3_threshold, red: this.config.nucmed_radcon1_threshold };
                break;
            case 'ultrasound':
                thresholds = { yellow: this.config.ultrasound_radcon5_threshold, orange: this.config.ultrasound_radcon3_threshold, red: this.config.ultrasound_radcon1_threshold };
                break;
            default:
                thresholds = { yellow: 15, orange: 35, red: 70 };
        }

        if (cases === 0) {
            return { level: 'green', text: 'Normal', class: 'bg-success' };
        } else if (cases <= thresholds.yellow) {
            return { level: 'yellow', text: 'Elevated', class: 'bg-warning' };
        } else if (cases <= thresholds.orange) {
            return { level: 'orange', text: 'High', class: 'bg-warning' };
        } else {
            return { level: 'red', text: 'Critical', class: 'bg-danger' };
        }
    }

    calculateTurnaroundTime(cases, type) {
        if (!this.config) return 0;
        
        // Use dynamic processing rates from configuration
        const processingRates = {
            mri: this.config.mri_processing_rate,
            ct: this.config.ct_processing_rate,
            xray: this.config.xray_processing_rate,
            nucmed: this.config.nucmed_processing_rate,
            ultrasound: this.config.ultrasound_processing_rate
        };

        if (cases === 0) return 0;
        
        // Apply radiologist staffing level (percentage) to processing rate
        const staffingMultiplier = (this.radiologistStaffing || 100) / 100;
        const effectiveProcessingRate = processingRates[type] * staffingMultiplier;
        
        return Math.ceil(cases / effectiveProcessingRate);
    }

    calculateOverallStatus(cases) {
        const total = cases.mri + cases.ct + cases.xray + cases.nucmed + cases.ultrasound;
        
        // Weighted scoring based on complexity (inverse system where 5 is normal, 1 is critical)
        const weightedScore = (cases.mri * 3) + (cases.ct * 2) + (cases.xray * 1) + (cases.nucmed * 4) + (cases.ultrasound * 2);
        
        if (total === 0) {
            return {
                level: 'Radcon 5',
                description: 'Very low demand',
                class: 'bg-radcon-5',
                radcon: 5
            };
        } else if (!this.config || weightedScore <= this.config.radcon_4_threshold) {
            return {
                level: 'Radcon 4',
                description: 'Low demand',
                class: 'bg-radcon-4',
                radcon: 4
            };
        } else if (weightedScore <= this.config.radcon_3_threshold) {
            return {
                level: 'Radcon 3',
                description: 'Average demand',
                class: 'bg-radcon-3',
                radcon: 3
            };
        } else if (weightedScore <= this.config.radcon_2_threshold) {
            return {
                level: 'Radcon 2',
                description: 'Above average demand',
                class: 'bg-radcon-2',
                radcon: 2
            };
        } else {
            return {
                level: 'Radcon 1',
                description: 'High demand',
                class: 'bg-radcon-1',
                radcon: 1
            };
        }
    }

    updateModalityDisplay(modality, cases, elements) {
        const status = this.calculateModalityStatus(cases, modality);
        const turnaround = this.calculateTurnaroundTime(cases, modality);

        // Update badge
        elements.badge.textContent = status.text;
        elements.badge.className = `badge ${status.class}`;

        // Update status dot
        elements.dot.className = `status-dot ${status.level}`;

        // Update case count
        elements.count.textContent = `${cases} case${cases !== 1 ? 's' : ''}`;

        // Update turnaround estimate
        elements.turnaround.textContent = `Est. ${turnaround} day${turnaround !== 1 ? 's' : ''}`;
    }

    updateSummaryStats(cases) {
        const total = cases.mri + cases.ct + cases.xray + cases.nucmed + cases.ultrasound;
        const mriTurnaround = this.calculateTurnaroundTime(cases.mri, 'mri');
        const ctTurnaround = this.calculateTurnaroundTime(cases.ct, 'ct');
        const xrayTurnaround = this.calculateTurnaroundTime(cases.xray, 'xray');
        const nucmedTurnaround = this.calculateTurnaroundTime(cases.nucmed, 'nucmed');
        const ultrasoundTurnaround = this.calculateTurnaroundTime(cases.ultrasound, 'ultrasound');
        
        const maxTurnaround = Math.max(mriTurnaround, ctTurnaround, xrayTurnaround, nucmedTurnaround, ultrasoundTurnaround);
        const avgTurnaround = total > 0 ? Math.round((mriTurnaround + ctTurnaround + xrayTurnaround + nucmedTurnaround + ultrasoundTurnaround) / 5) : 0;

        // Update average turnaround
        this.avgTurnaround.textContent = avgTurnaround;

        // Update workload assessment
        let workloadText, workloadClass;
        if (total === 0) {
            workloadText = 'Normal';
            workloadClass = 'text-success';
        } else if (total <= 50) {
            workloadText = 'Light';
            workloadClass = 'text-info';
        } else if (total <= 120) {
            workloadText = 'Moderate';
            workloadClass = 'text-warning';
        } else {
            workloadText = 'Heavy';
            workloadClass = 'text-danger';
        }
        
        this.workload.textContent = workloadText;
        this.workload.className = `mb-1 ${workloadClass}`;


    }

    updateDashboard() {
        const cases = this.getCaseValues();
        
        // Update case count displays
        this.displayMriCases.textContent = cases.mri;
        this.displayCtCases.textContent = cases.ct;
        this.displayXrayCases.textContent = cases.xray;
        this.displayNucmedCases.textContent = cases.nucmed;
        this.displayUltrasoundCases.textContent = cases.ultrasound;
        
        // Update total cases in header
        const total = cases.mri + cases.ct + cases.xray + cases.nucmed + cases.ultrasound;
        this.totalCasesHeader.textContent = total;
        
        // Update individual modality displays
        this.updateModalityDisplay('mri', cases.mri, this.mriElements);
        this.updateModalityDisplay('ct', cases.ct, this.ctElements);
        this.updateModalityDisplay('xray', cases.xray, this.xrayElements);
        this.updateModalityDisplay('nucmed', cases.nucmed, this.nucmedElements);
        this.updateModalityDisplay('ultrasound', cases.ultrasound, this.ultrasoundElements);

        // Calculate overall status
        const overallStatus = this.calculateOverallStatus(cases);
        
        // Update overall status display
        this.statusLevel.textContent = overallStatus.level;
        this.statusDescription.textContent = overallStatus.description;
        
        // Update status circle
        this.statusCircle.className = `status-circle ${overallStatus.class}`;
        
        // Add pulse animation for high demand status (Radcon 1-2)
        if (overallStatus.radcon <= 2) {
            this.statusCircle.classList.add('pulse');
        } else {
            this.statusCircle.classList.remove('pulse');
        }

        // Calculate and display overall turnaround
        const mriTurnaround = this.calculateTurnaroundTime(cases.mri, 'mri');
        const ctTurnaround = this.calculateTurnaroundTime(cases.ct, 'ct');
        const xrayTurnaround = this.calculateTurnaroundTime(cases.xray, 'xray');
        const nucmedTurnaround = this.calculateTurnaroundTime(cases.nucmed, 'nucmed');
        const ultrasoundTurnaround = this.calculateTurnaroundTime(cases.ultrasound, 'ultrasound');
        const maxTurnaround = Math.max(mriTurnaround, ctTurnaround, xrayTurnaround, nucmedTurnaround, ultrasoundTurnaround);
        
        this.turnaroundTime.textContent = `${maxTurnaround} day${maxTurnaround !== 1 ? 's' : ''}`;
        
        // Update turnaround note based on status
        let noteText;
        if (maxTurnaround === 0) {
            noteText = 'No reporting turnaround required';
        } else if (maxTurnaround <= 2) {
            noteText = 'Normal reporting timeline';
        } else if (maxTurnaround <= 5) {
            noteText = 'Extended reporting time required';
        } else {
            noteText = 'Urgent: Additional resources needed';
        }
        
        this.turnaroundNote.textContent = noteText;

        // Update summary statistics
        this.updateSummaryStats(cases);

        // Update turnaround time color based on urgency
        const turnaroundClasses = ['text-primary', 'text-success', 'text-info', 'text-warning', 'text-danger'];
        this.turnaroundTime.className = turnaroundClasses[Math.min(Math.floor(maxTurnaround / 2), 4)] + ' mb-2';
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AffinityDashboard();
    console.log('Affinity Reporting Status Dashboard initialized successfully');
});
