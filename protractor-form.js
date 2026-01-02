/**
 * Arc Protractor Generator - Form Handler with Custom Null Points
 * Place this file in: /templates/cassiopeia_escuta_home/js/
 */

(function() {
    'use strict';
    
    // Null point calculations for each alignment type
    // NOTE: These are optimized values for IEC standard groove radii (60.325-146.05mm)
    // Changing groove radii with standard alignments uses these same null points
    // For true custom groove optimization, use "Custom" alignment and enter null points manually
    const NULL_POINT_CALCULATIONS = {
        baerwald: function(pivotDistance, innerGroove, outerGroove) {
            // Baerwald (Löfgren A) - empirically derived optimal values for IEC grooves
            return {
                inner: '66.04',
                outer: '120.90'
            };
        },
        
        lofgren_b: function(pivotDistance, innerGroove, outerGroove) {
            // Löfgren B - empirically derived optimal values for IEC grooves
            return {
                inner: '70.29',
                outer: '116.60'
            };
        },
        
        stevenson: function(pivotDistance, innerGroove, outerGroove) {
            // Stevenson - inner null at innermost groove
            return {
                inner: '60.33',
                outer: '117.42'
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

        // Check if form exists on this page
        if (!form) {
            return; // Not on protractor form page
        }

        console.log('Protractor form initialized with null point support');

        // Update null points when alignment or groove values change
        function updateNullPoints() {
            const alignment = alignmentSelect.value;
            
            if (alignment === 'custom') {
                // Clear null points for custom entry
                innerNullInput.value = '';
                outerNullInput.value = '';
                innerNullInput.setAttribute('required', 'required');
                outerNullInput.setAttribute('required', 'required');
                innerNullInput.readOnly = false;
                outerNullInput.readOnly = false;
                innerNullInput.style.backgroundColor = '';
                outerNullInput.style.backgroundColor = '';
            } else {
                // Use standard null points for standard alignments
                const calculation = NULL_POINT_CALCULATIONS[alignment];
                if (calculation) {
                    const pivotDistance = parseFloat(pivotDistanceInput.value) || 0;
                    const innerGroove = parseFloat(innerGrooveInput.value) || 60.325;
                    const outerGroove = parseFloat(outerGrooveInput.value) || 146.05;
                    
                    const nullPoints = calculation(pivotDistance, innerGroove, outerGroove);
                    innerNullInput.value = parseFloat(nullPoints.inner);
                    outerNullInput.value = parseFloat(nullPoints.outer);
                    innerNullInput.removeAttribute('required');
                    outerNullInput.removeAttribute('required');
                    innerNullInput.readOnly = true;
                    outerNullInput.readOnly = true;
                    innerNullInput.style.backgroundColor = '#f0f0f0';
                    outerNullInput.style.backgroundColor = '#f0f0f0';
                }
            }
        }

        // Attach listeners
        alignmentSelect.addEventListener('change', updateNullPoints);
        pivotDistanceInput.addEventListener('input', updateNullPoints);
        innerGrooveInput.addEventListener('input', updateNullPoints);
        outerGrooveInput.addEventListener('input', updateNullPoints);

        // Initialize null points on page load
        updateNullPoints();

        // Form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Validate required fields
            const pivotDistance = pivotDistanceInput.value;
            const innerGroove = innerGrooveInput.value;
            const outerGroove = outerGrooveInput.value;
            
            if (!pivotDistance || !innerGroove || !outerGroove) {
                messageDiv.className = 'alert alert-error';
                messageDiv.innerHTML = '✗ Please fill in all required fields';
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
