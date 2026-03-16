// assets/script.js

function toggleDetail(id) {
    var detailRow = document.getElementById(id);
    if(detailRow) {
        detailRow.style.display = detailRow.style.display === "none" ? "table-row" : "none";
    }
}

function toggleCard(id) {
    var detailList = document.getElementById(id);
    if(detailList) {
        detailList.style.display = detailList.style.display === "none" ? "block" : "none";
    }
}

function filtrarTabela(status, btnElement) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.className = "filter-btn");
    btnElement.classList.add('active-' + status);
    
    document.querySelectorAll('.printer-row').forEach(row => {
        let rowStatus = row.getAttribute('data-status');
        let targetId = row.getAttribute('onclick').match(/'([^']+)'/)[1];
        let detailRow = document.getElementById(targetId);
        
        if (status === 'all' || rowStatus === status) { 
            row.style.display = ''; 
        } else { 
            row.style.display = 'none'; 
            if(detailRow) detailRow.style.display = 'none'; 
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if(searchInput) {
        searchInput.addEventListener('keyup', function() {
            let filter = this.value.toLowerCase();
            document.querySelectorAll('.printer-row').forEach(row => {
                let text = row.innerText.toLowerCase();
                let targetId = row.getAttribute('onclick').match(/'([^']+)'/)[1];
                let detailRow = document.getElementById(targetId);
                
                if(text.includes(filter)) { 
                    row.style.display = ''; 
                } else { 
                    row.style.display = 'none'; 
                    if(detailRow) detailRow.style.display = 'none'; 
                }
            });
        });
    }
});