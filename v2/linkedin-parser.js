// Parse LinkedIn CSV export data
// Used by MasterCVEditor to import work history, education, skills from LinkedIn
const parseLinkedInCSV = (csvText, type) => {
    const lines = csvText.split('\n');
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/"/g, ''));
    const results = [];

    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;

        // Handle CSV with quoted fields
        const values = [];
        let current = '';
        let inQuotes = false;
        for (const char of lines[i]) {
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                values.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        values.push(current.trim());

        const row = {};
        headers.forEach((h, idx) => {
            row[h] = values[idx] || '';
        });
        results.push(row);
    }
    return results;
};
