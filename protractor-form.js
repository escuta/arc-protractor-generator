/**
 * Arc Protractor Generator - Form Handler with Custom Null Points
 * Place this file in: /templates/cassiopeia_escuta_home/js/
 */

(function() {
    'use strict';
    
    // Null point calculations for each alignment type
    // For IEC standard grooves (60.325-146.05mm), these return exact published values.
    // For other groove radii, they scale proportionally to maintain distortion balance.
    const NULL_POINT_CALCULATIONS = {
        baerwald: function(pivotDistance, innerGroove, outerGroove) {
            // Baerwald (Löfgren A) - minimizes maximum tracking error
            const r_in = parseFloat(innerGroove);
            const r_out = parseFloat(outerGroove);
            
            // IEC standard reference values
            const IEC_INNER = 60.325;
            const IEC_OUTER = 146.05;
            const IEC_N1 = 66.04;
            const IEC_N2 = 120.90;
            
            // For IEC standard grooves, use exact values
            if (Math.abs(r_in - IEC_INNER) < 0.01 && Math.abs(r_out - IEC_OUTER) < 0.01) {
                return {
                    inner: IEC_N1.toFixed(2),
                    outer: IEC_N2.toFixed(2)
                };
            }
            
            // Scale null points proportionally for non-standard groove radii
            const scaleFactor = Math.sqrt((r_out - r_in) / (IEC_OUTER - IEC_INNER));
            const offsetInner = IEC_N1 - IEC_INNER;
            const offsetOuter = IEC_OUTER - IEC_N2;
            
            const innerNull = r_in + offsetInner * scaleFactor;
            const outerNull = r_out - offsetOuter * scaleFactor;
            
            return {
                inner: innerNull.toFixed(2),
                outer: outerNull.toFixed(2)
            };
        },
        
        lofgren_b: function(pivotDistance, innerGroove, outerGroove) {
            // Löfgren B - minimizes RMS (average) tracking error
            const r_in = parseFloat(innerGroove);
            const r_out = parseFloat(outerGroove);
            
            // IEC standard reference values
            const IEC_INNER = 60.325;
            const IEC_OUTER = 146.05;
            const IEC_N1 = 70.29;
            const IEC_N2 = 116.60;
            
            // For IEC standard grooves, use exact values
            if (Math.abs(r_in - IEC_INNER) < 0.01 && Math.abs(r_out - IEC_OUTER) < 0.01) {
                return {
                    inner: IEC_N1.toFixed(2),
                    outer: IEC_N2.toFixed(2)
                };
            }
            
            // Scale null points proportionally for non-standard groove radii
            const scaleFactor = Math.sqrt((r_out - r_in) / (IEC_OUTER - IEC_INNER));
            const offsetInner = IEC_N1 - IEC_INNER;
            const offsetOuter = IEC_OUTER - IEC_N2;
            
            const innerNull = r_in + offsetInner * scaleFactor;
            const outerNull = r_out - offsetOuter * scaleFactor;
            
            return {
                inner: innerNull.toFixed(2),
                outer: outerNull.toFixed(2)
            };
        },
        
        stevenson: function(pivotDistance, innerGroove, outerGroove) {
            // Stevenson - minimizes distortion at inner grooves
            // Inner null always at innermost groove
            const r_in = parseFloat(innerGroove);
            const r_out = parseFloat(outerGroove);
            
            // IEC standard reference values
            const IEC_INNER = 60.325;
            const IEC_OUTER = 146.05;
            
            const innerNull = r_in;
            
            // For IEC standard grooves, use known optimal value
            if (Math.abs(r_in - IEC_INNER) < 0.01 && Math.abs(r_out - IEC_OUTER) < 0.01) {
                const outerNull = 117.42;
                return {
                    inner: innerNull.toFixed(2),
                    outer: outerNull.toFixed(2)
                };
            }
            
            // For non-standard grooves, use geometric mean approximation
            const outerNull = Math.sqrt(r_in * r_out);
            
            return {
                inner: innerNull.toFixed(2),
                outer: outerNull.toFixed(2)
            };
        }
    };
    
    // Wait for DOM to be ready
    function initProtractorForm() {
        const form = document.getElementById('protractorForm');
        const alignmentSelect = document.getElementById('alignment');
        const pivotDistanceInput = document.getElementById('pivot_distance');
        const innerGrooveInput = document.getElementById('inner_groove');
        const outerGrooveInput = document.getElementById('outer_groove');
        const innerNullInput = document.getElementById('inner_null');
        const outerNullInput = document.getElementById('outer_null');
        const messageDiv = document.getElementById('message');
        const generateBtn = document.getElementById('generateBtn');
        const grooveStandardSelect = document.getElementById('groove_standard');

        // Check if form exists on this page
        if (!form) {
            return; // Not on protractor form page
        }

        // Verify all required elements exist
        const requiredElements = {
            'form': form,
            'alignmentSelect': alignmentSelect,
            'pivotDistanceInput': pivotDistanceInput,
            'innerGrooveInput': innerGrooveInput,
            'outerGrooveInput': outerGrooveInput,
            'innerNullInput': innerNullInput,
            'outerNullInput': outerNullInput,
            'grooveStandardSelect': grooveStandardSelect
        };

        for (const [name, element] of Object.entries(requiredElements)) {
            if (!element || (element.length !== undefined && element.length === 0)) {
                console.error('Protractor form: Missing required element:', name);
                return;
            }
        }

        console.log('Protractor form initialized successfully');

        // Groove standard presets
        const GROOVE_STANDARDS = {
            iec: { inner: 60.325, outer: 146.05 },
            din: { inner: 57.5, outer: 146.05 }
        };

        // Handle groove standard dropdown changes
        function handleGrooveStandardChange(event) {
            console.log('Groove standard change triggered');
            
            const selectedStandard = grooveStandardSelect.value;
            console.log('Selected groove standard:', selectedStandard);
            
            if (selectedStandard === 'custom') {
                // Custom - don't change current values
                console.log('Custom selected, keeping current groove values');
                return;
            }
            
            if (GROOVE_STANDARDS[selectedStandard]) {
                console.log('Applying standard values:', GROOVE_STANDARDS[selectedStandard]);
                innerGrooveInput.value = GROOVE_STANDARDS[selectedStandard].inner;
                outerGrooveInput.value = GROOVE_STANDARDS[selectedStandard].outer;
                updateNullPoints();
            } else {
                console.error('Unknown groove standard:', selectedStandard);
            }
        }
        
        // Switch to Custom when user manually edits groove radii
        function handleGrooveRadiiEdit() {
            const selectedStandard = grooveStandardSelect.value;
            
            // Check if current values match any standard
            const currentInner = parseFloat(innerGrooveInput.value);
            const currentOuter = parseFloat(outerGrooveInput.value);
            
            console.log('handleGrooveRadiiEdit:', {
                currentInner: currentInner,
                currentOuter: currentOuter,
                selectedStandard: selectedStandard
            });
            
            let matchesStandard = false;
            for (const [key, values] of Object.entries(GROOVE_STANDARDS)) {
                if (Math.abs(currentInner - values.inner) < 0.01 && 
                    Math.abs(currentOuter - values.outer) < 0.01) {
                    matchesStandard = true;
                    console.log('Matches standard:', key);
                    break;
                }
            }
            
            // If values don't match any standard, switch to Custom
            if (!matchesStandard && selectedStandard !== 'custom') {
                console.log('Switching to custom groove standard');
                grooveStandardSelect.value = 'custom';
            }
        }

        // Update null points when alignment or groove values change
        function updateNullPoints() {
            const alignment = alignmentSelect.value;
            
            console.log('updateNullPoints called:', {
                alignment: alignment,
                innerGroove: innerGrooveInput.value,
                outerGroove: outerGrooveInput.value,
                pivotDistance: pivotDistanceInput.value
            });
            
            if (alignment === 'custom') {
                // In Custom alignment mode, don't touch the null points
                // User has manually entered them
                console.log('Alignment is custom, skipping null point calculation');
                innerNullInput.setAttribute('required', 'required');
                outerNullInput.setAttribute('required', 'required');
                return;
            }
            
            // Calculate null points for standard alignments
            const calculation = NULL_POINT_CALCULATIONS[alignment];
            if (!calculation) {
                console.error('Unknown alignment type:', alignment);
                return;
            }
            
            const pivotDistance = parseFloat(pivotDistanceInput.value) || 0;
            const innerGroove = parseFloat(innerGrooveInput.value);
            const outerGroove = parseFloat(outerGrooveInput.value);
            
            // Only calculate if we have valid groove values
            if (isNaN(innerGroove) || isNaN(outerGroove)) {
                console.log('Invalid groove values, skipping calculation');
                return;
            }
            
            const nullPoints = calculation(pivotDistance, innerGroove, outerGroove);
            console.log('Calculated null points:', nullPoints);
            
            innerNullInput.value = nullPoints.inner;
            outerNullInput.value = nullPoints.outer;
            innerNullInput.removeAttribute('required');
            outerNullInput.removeAttribute('required');
        }
        
        // Switch to Custom mode when user edits null points
        function handleNullPointEdit() {
            if (alignmentSelect.value !== 'custom') {
                alignmentSelect.value = 'custom';
                innerNullInput.setAttribute('required', 'required');
                outerNullInput.setAttribute('required', 'required');
            }
        }

        // Handle alignment dropdown changes
        function handleAlignmentChange() {
            // If user explicitly selects Custom from dropdown, clear the null fields
            if (alignmentSelect.value === 'custom') {
                innerNullInput.value = '';
                outerNullInput.value = '';
            }
            updateNullPoints();
        }
        
        // Attach listeners
        grooveStandardSelect.addEventListener('change', handleGrooveStandardChange);
        alignmentSelect.addEventListener('change', handleAlignmentChange);
        pivotDistanceInput.addEventListener('input', updateNullPoints);
        innerGrooveInput.addEventListener('input', function() {
            handleGrooveRadiiEdit();
            updateNullPoints();
        });
        outerGrooveInput.addEventListener('input', function() {
            handleGrooveRadiiEdit();
            updateNullPoints();
        });
        
        // Switch to Custom when user manually edits null points
        innerNullInput.addEventListener('input', handleNullPointEdit);
        outerNullInput.addEventListener('input', handleNullPointEdit);

        // Initialize null points on page load
        updateNullPoints();

        // Form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Validate required fields
            const pivotDistance = parseFloat(pivotDistanceInput.value);
            const innerGroove = parseFloat(innerGrooveInput.value);
            const outerGroove = parseFloat(outerGrooveInput.value);
            const innerNull = parseFloat(innerNullInput.value);
            const outerNull = parseFloat(outerNullInput.value);
            
            if (!pivotDistance || !innerGroove || !outerGroove) {
                messageDiv.className = 'alert alert-error';
                messageDiv.innerHTML = '✗ Please fill in all required fields';
                messageDiv.style.display = 'block';
                return;
            }

            // Validate null points are within valid ranges
            // Note: Stevenson alignment allows inner_null == inner_groove by design
            // Use small tolerance for floating point comparison
            const tolerance = 0.001; // 1 micron tolerance
            
            if (innerNull < (innerGroove - tolerance)) {
                messageDiv.className = 'alert alert-error';
                messageDiv.innerHTML = '✗ Inner null point (' + innerNull + 'mm) must be greater than or equal to inner groove radius (' + innerGroove + 'mm)';
                messageDiv.style.display = 'block';
                return;
            }
            
            if (outerNull >= outerGroove) {
                messageDiv.className = 'alert alert-error';
                messageDiv.innerHTML = '✗ Outer null point (' + outerNull + 'mm) must be less than outer groove radius (' + outerGroove + 'mm)';
                messageDiv.style.display = 'block';
                return;
            }
            
            if (innerNull >= outerNull) {
                messageDiv.className = 'alert alert-error';
                messageDiv.innerHTML = '✗ Inner null point (' + innerNull + 'mm) must be less than outer null point (' + outerNull + 'mm)';
                messageDiv.style.display = 'block';
                return;
            }

            // Show loading state
            generateBtn.disabled = true;
            generateBtn.innerHTML = generateBtn.getAttribute('data-loading-text') || 'Generating...';
            
            messageDiv.style.display = 'none';
            messageDiv.className = 'alert';

            // Collect form data
            const formData = new FormData();
            formData.append('pivot_distance', pivotDistance);
            formData.append('alignment', alignmentSelect.value);
            formData.append('turntable_name', document.getElementById('turntable_name').value);
            formData.append('paper_size', document.getElementById('paper_size').value);
            
            // Add language parameter from hidden field
            const languageInput = document.getElementById('language');
            if (languageInput) {
                formData.append('language', languageInput.value);
            }
            
            // Always send groove values
            formData.append('inner_groove', innerGroove);
            formData.append('outer_groove', outerGroove);
            
            // Add null points for custom alignment
            if (alignmentSelect.value === 'custom') {
                formData.append('inner_null', innerNullInput.value);
                formData.append('outer_null', outerNullInput.value);
            }
            
            // Debug log
            console.log('Submitting form data:', {
                pivot_distance: pivotDistance,
                alignment: alignmentSelect.value,
                inner_groove: innerGroove,
                outer_groove: outerGroove,
                inner_null: innerNullInput.value,
                outer_null: outerNullInput.value
            });

            // Send to backend
            fetch('/protractor/generate-protractor.php', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Generation failed');
                    });
                }
                return response.blob();
            })
            .then(blob => {
                // Create blob URL and open in new tab
                const url = window.URL.createObjectURL(blob);
                
                // Open PDF in new tab
                const newTab = window.open(url, '_blank');
                
                // Only show message if popup was blocked
                if (!newTab) {
                    messageDiv.className = 'alert alert-info';
                    messageDiv.innerHTML = generateBtn.getAttribute('data-blocked-text') || 
                        'Popup blocked! <a href="' + url + '" target="_blank">Click here to open your protractor</a>';
                    messageDiv.style.display = 'block';
                }
                
                // Clean up URL after 1 minute
                setTimeout(() => window.URL.revokeObjectURL(url), 60000);

                // Reset button
                generateBtn.disabled = false;
                generateBtn.innerHTML = generateBtn.getAttribute('data-button-text') || 'Generate Protractor';
            })
            .catch(error => {
                // Show error message
                messageDiv.className = 'alert alert-error';
                messageDiv.innerHTML = '✗ Error: ' + error.message;
                messageDiv.style.display = 'block';

                // Reset button
                generateBtn.disabled = false;
                generateBtn.innerHTML = generateBtn.getAttribute('data-button-text') || 'Generate Protractor';
            });
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProtractorForm);
    } else {
        initProtractorForm();
    }
})();
