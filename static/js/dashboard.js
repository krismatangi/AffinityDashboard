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
                mri_yellow: 10, mri_orange: 25, mri_red: 50,
                ct_yellow: 15, ct_orange: 35, ct_red: 70,
                xray_yellow: 25, xray_orange: 60, xray_red: 120,
                nucmed_yellow: 8, nucmed_orange: 20, nucmed_red: 40,
                ultrasound_yellow: 15, ultrasound_orange: 40, ultrasound_red: 80,
                mri_rate: 8, ct_rate: 12, xray_rate: 20, nucmed_rate: 6, ultrasound_rate: 10,
                radcon_4_threshold: 30, radcon_3_threshold: 60, radcon_2_threshold: 100
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
            
            this.updateLastUpdatedTime(data.updated_at, data.updated_by);
            this.updateDashboard();
            
        } catch (error) {
            console.error('Error loading case data:', error);
            this.showError('Unable to load current case data');
        }
    }

    setupAutoRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            this.loadCaseData();
        }, 30000);
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
        
        // Use dynamic thresholds from configuration
        switch(type) {
            case 'mri':
                thresholds = { yellow: this.config.mri_yellow, orange: this.config.mri_orange, red: this.config.mri_red };
                break;
            case 'ct':
                thresholds = { yellow: this.config.ct_yellow, orange: this.config.ct_orange, red: this.config.ct_red };
                break;
            case 'xray':
                thresholds = { yellow: this.config.xray_yellow, orange: this.config.xray_orange, red: this.config.xray_red };
                break;
            case 'nucmed':
                thresholds = { yellow: this.config.nucmed_yellow, orange: this.config.nucmed_orange, red: this.config.nucmed_red };
                break;
            case 'ultrasound':
                thresholds = { yellow: this.config.ultrasound_yellow, orange: this.config.ultrasound_orange, red: this.config.ultrasound_red };
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
            mri: this.config.mri_rate,
            ct: this.config.ct_rate,
            xray: this.config.xray_rate,
            nucmed: this.config.nucmed_rate,
            ultrasound: this.config.ultrasound_rate
        };

        if (cases === 0) return 0;
        
        return Math.ceil(cases / processingRates[type]);
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
