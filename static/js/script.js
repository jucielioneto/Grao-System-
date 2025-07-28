// Service Worker Registration
if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("/static/service-worker.js")
    .then(function (registration) {
      console.log(
        "Service Worker registrado com sucesso:",
        registration.scope
      );
    })
    .catch(function (err) {
      console.log("Falha ao registrar o Service Worker:", err);
    });
}

// Dropdown functionality
const dropdownToggle = document.getElementById('dropdownMenu');
const dropdownMenu = document.getElementById('dropdownMenuContent');
const dropdownItems = document.querySelectorAll('.dropdown-item');

// Initialize with correct section only if we're on the main page
document.addEventListener('DOMContentLoaded', function() {
    const currentSectionElement = document.getElementById('currentSection');
    if (currentSectionElement && dropdownToggle && dropdownItems.length > 0) {
        const currentSection = currentSectionElement.value;
        const activeItem = document.querySelector(`[data-section="${currentSection}"]`);
        if (activeItem) {
            // Remove active class from all items
            dropdownItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to current section
            activeItem.classList.add('active');
            
            // Update dropdown toggle text
            const dropdownText = activeItem.textContent.trim();
            dropdownToggle.innerHTML = `${dropdownText} <i class="fas fa-chevron-down"></i>`;
            
            // Handle section change
            handleSectionChange(currentSection);
        }
    }
});

// Toggle dropdown
if (dropdownToggle) {
    dropdownToggle.addEventListener('click', function(e) {
        e.preventDefault();
        const dropdown = this.closest('.dropdown');
        dropdown.classList.toggle('active');
    });
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    const dropdown = document.querySelector('.dropdown');
    if (dropdown && !e.target.closest('.dropdown')) {
        dropdown.classList.remove('active');
    }
});

// Handle dropdown item clicks
dropdownItems.forEach(item => {
    item.addEventListener('click', function(e) {
        // Check if we're on the main page (index)
        const isMainPage = window.location.pathname === '/' || window.location.pathname === '/index';
        
        if (isMainPage) {
            // If we're on the main page, handle section change locally
            e.preventDefault();
            
            // Remove active class from all items
            dropdownItems.forEach(i => i.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Update dropdown toggle text
            const dropdownText = this.textContent.trim();
            if (dropdownToggle) {
                dropdownToggle.innerHTML = `${dropdownText} <i class="fas fa-chevron-down"></i>`;
            }
            
            // Close dropdown
            const dropdown = document.querySelector('.dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
            
            // Handle section change only if we're on the main page
            const section = this.getAttribute('data-section');
            const currentSectionElement = document.getElementById('currentSection');
            if (currentSectionElement) {
                handleSectionChange(section);
            }
        } else {
            // If we're not on the main page, let the link work normally (no preventDefault)
            // Just close the dropdown
            const dropdown = document.querySelector('.dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
        }
    });
});

// Handle section change - only for main page
function handleSectionChange(section) {
    const cardHeader = document.querySelector('.card-header h2');
    const sectionHeader = document.querySelector('.section-header h3');
    const uploadDescription = document.getElementById('uploadDescription');
    const fileInput = document.getElementById('fileInput');
    const currentSection = document.getElementById('currentSection');
    
    // Only proceed if we're on the main page
    if (!cardHeader || !sectionHeader || !uploadDescription || !fileInput || !currentSection) {
        return;
    }
    
    // Update hidden field
    currentSection.value = section;
    
    if (section === 'pituba') {
        cardHeader.textContent = 'Sistema de Processamento: Pedidos Pituba';
        sectionHeader.textContent = 'Produtos para Pituba';
        uploadDescription.textContent = 'Arraste e solte ou clique para selecionar arquivos .xls ou .xlsx';
        fileInput.multiple = true;
    } else if (section === 'hortifruti') {
        cardHeader.textContent = 'Sistema de Processamento: Pedidos Hortifruti';
        sectionHeader.textContent = 'Produtos Hortifruti por Loja';
        uploadDescription.textContent = 'Selecione um arquivo Excel para processar pedidos de múltiplas lojas';
        fileInput.multiple = false;
    }
    
    // Clear any existing results
    const productsSection = document.getElementById('productsSection');
    const hortifrutiProductsSection = document.getElementById('hortifrutiProductsSection');
    const downloadsSection = document.getElementById('downloadsSection');
    const selectedFiles = document.getElementById('selectedFiles');
    
    if (productsSection) productsSection.style.display = 'none';
    if (hortifrutiProductsSection) hortifrutiProductsSection.style.display = 'none';
    if (downloadsSection) downloadsSection.style.display = 'none';
    if (selectedFiles) {
        selectedFiles.style.display = 'none';
        selectedFiles.innerHTML = '';
    }
    if (fileInput) fileInput.value = '';
}

// File input handling - only for main page
const fileInput = document.getElementById('fileInput');
if (fileInput) {
    fileInput.addEventListener('change', function(e) {
        const selectedFiles = document.getElementById('selectedFiles');
        if (!selectedFiles) return;
        
        selectedFiles.innerHTML = '';
        
        if (e.target.files.length > 0) {
            selectedFiles.style.display = 'block';
            
            Array.from(e.target.files).forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <i class="fas fa-file-excel"></i>
                    <span>${file.name}</span>
                    <span class="file-size">(${(file.size / 1024).toFixed(1)} KB)</span>
                `;
                selectedFiles.appendChild(fileItem);
            });
        } else {
            selectedFiles.style.display = 'none';
        }
    });
}

// Drag and drop functionality - only for main page
const uploadArea = document.querySelector('.file-upload-area');

if (uploadArea) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        uploadArea.classList.add('drag-over');
    }

    function unhighlight(e) {
        uploadArea.classList.remove('drag-over');
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.files = files;
            
            // Trigger change event
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    }
}

// Form submission handling - only for main page
const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const processBtn = document.getElementById('processBtn');
        const originalText = processBtn.innerHTML;
        
        // Show loading state
        processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        processBtn.disabled = true;
        
        fetch('/processar', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading state
            processBtn.innerHTML = originalText;
            processBtn.disabled = false;
            
            if (data.error) {
                alert(data.error);
                return;
            }
            
            // Handle different sections
            if (data.section === 'hortifruti') {
                handleHortifrutiResponse(data);
            } else {
                handlePitubaResponse(data);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            processBtn.innerHTML = originalText;
            processBtn.disabled = false;
            alert('Erro ao processar os arquivos. Tente novamente.');
        });
    });
}

// Handle Hortifruti response - only for main page
function handleHortifrutiResponse(data) {
    const hortifrutiProductsSection = document.getElementById('hortifrutiProductsSection');
    const productsSection = document.getElementById('productsSection');
    const downloadsSection = document.getElementById('downloadsSection');
    
    if (!hortifrutiProductsSection || !productsSection || !downloadsSection) return;
    
    // Show products section first
    hortifrutiProductsSection.style.display = 'block';
    productsSection.style.display = 'none';
    downloadsSection.style.display = 'none';
    
    // Update summary
    const summaryElement = document.getElementById('hortifrutiProductsSummary');
    if (summaryElement) {
        summaryElement.textContent = 
            `Total de ${data.total_produtos} produtos processados para ${data.arquivos_gerados.length} lojas`;
    }
    
    // Populate Hortifruti products table
    const tableBody = document.getElementById('hortifrutiProductsTableBody');
    if (tableBody) {
        tableBody.innerHTML = '';
        
        data.produtos.forEach(produto => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="product-code">${produto.codigo}</span></td>
                <td><span class="product-name">${produto.nome}</span></td>
                <td><span class="product-quantity">${produto.quantidades.vilas || 0}</span></td>
                <td><span class="product-quantity">${produto.quantidades.vitoria || 0}</span></td>
                <td><span class="product-quantity">${produto.quantidades.pituba || 0}</span></td>
                <td><span class="product-quantity">${produto.quantidades.apipema || 0}</span></td>
                <td><span class="product-file">${produto.arquivo_origem}</span></td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    // Show downloads section
    downloadsSection.style.display = 'block';
    
    // Update downloads summary
    const downloadsSummary = document.getElementById('downloadsSummary');
    if (downloadsSummary) {
        downloadsSummary.textContent = 
            `${data.arquivos_gerados.length} arquivos gerados com ${data.total_produtos} produtos processados`;
    }
    
    // Populate downloads grid
    const downloadsGrid = document.getElementById('downloadsGrid');
    if (downloadsGrid) {
        downloadsGrid.innerHTML = '';
        
        data.arquivos_gerados.forEach(arquivo => {
            const downloadItem = document.createElement('div');
            downloadItem.className = 'download-item';
            downloadItem.innerHTML = `
                <i class="fas fa-file-text"></i>
                <h4>${arquivo}</h4>
                <p>Arquivo TXT gerado</p>
                <a href="/baixar/${arquivo}" class="download-item-btn">
                    <i class="fas fa-download"></i> Baixar
                </a>
            `;
            downloadsGrid.appendChild(downloadItem);
        });
    }
    
    // Scroll to products section
    hortifrutiProductsSection.scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// Handle Pituba response - only for main page
function handlePitubaResponse(data) {
    const productsSection = document.getElementById('productsSection');
    const hortifrutiProductsSection = document.getElementById('hortifrutiProductsSection');
    const downloadsSection = document.getElementById('downloadsSection');
    
    if (!productsSection || !hortifrutiProductsSection || !downloadsSection) return;
    
    // Show products section
    productsSection.style.display = 'block';
    hortifrutiProductsSection.style.display = 'none';
    downloadsSection.style.display = 'none';
    
    // Update summary based on current section
    const activeSection = document.querySelector('.dropdown-item.active');
    if (activeSection) {
        const sectionName = activeSection.getAttribute('data-section') === 'pituba' ? 'Pituba' : 'Hortifruti';
        const productsSummary = document.getElementById('productsSummary');
        if (productsSummary) {
            productsSummary.textContent = 
                `Total de ${data.total_produtos} produtos processados para ${sectionName}`;
        }
    }
    
    // Populate table
    const tableBody = document.getElementById('productsTableBody');
    if (tableBody) {
        tableBody.innerHTML = '';
        
        data.produtos.forEach(produto => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="product-code">${produto.codigo}</span></td>
                <td><span class="product-name">${produto.nome}</span></td>
                <td><span class="product-quantity">${produto.quantidade.toLocaleString('pt-BR')}</span></td>
                <td><span class="product-file">${produto.arquivo_origem}</span></td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    // Show download button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'inline-flex';
        downloadBtn.onclick = function() {
            window.location.href = `/baixar/${data.arquivo_txt}`;
        };
    }
    
    // Scroll to products section
    productsSection.scrollIntoView({ 
        behavior: 'smooth' 
    });
}

// Profile Dropdown functionality
const profileDropdown = document.getElementById('profileDropdown');
const profileMenu = document.getElementById('profileMenu');

// Toggle profile dropdown
if (profileDropdown && profileMenu) {
    profileDropdown.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const dropdown = this.closest('.profile-dropdown');
        dropdown.classList.toggle('active');
    });

    // Close profile dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.profile-dropdown')) {
            const profileDropdowns = document.querySelectorAll('.profile-dropdown');
            profileDropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    // Close profile dropdown when clicking on menu items
    const profileItems = document.querySelectorAll('.profile-item');
    profileItems.forEach(item => {
        item.addEventListener('click', function() {
            const dropdown = this.closest('.profile-dropdown');
            dropdown.classList.remove('active');
        });
    });
}

// Modal Functions
function abrirModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function fecharModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Fechar modal ao clicar fora dele
window.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// Visualizar Planilha
function visualizarPlanilha(planilhaId) {
    console.log('Iniciando visualização da planilha:', planilhaId);
    abrirModal('planilhaModal');
    
    // Mostrar loading
    document.getElementById('planilhaLoading').style.display = 'block';
    document.getElementById('planilhaContent').style.display = 'none';
    document.getElementById('planilhaError').style.display = 'none';
    
    fetch(`/visualizar_planilha/${planilhaId}`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Dados recebidos:', data);
            document.getElementById('planilhaLoading').style.display = 'none';
            
            if (data.error) {
                console.error('Erro retornado:', data.error);
                document.getElementById('planilhaError').style.display = 'block';
                document.getElementById('planilhaErrorMessage').textContent = data.error;
                return;
            }
            
            // Preencher informações do arquivo
            document.getElementById('planilhaNome').textContent = data.nome_arquivo;
            document.getElementById('planilhaTotalLinhas').textContent = data.total_produtos;
            
            // Criar cabeçalhos da tabela baseado no tipo de processamento
            const thead = document.getElementById('planilhaTableHead');
            let headers = '';
            
            if (data.tipo_processamento === 'pituba') {
                headers = '<tr><th>Código</th><th>Nome do Produto</th><th>Quantidade</th><th>Loja de Destino</th></tr>';
            } else if (data.tipo_processamento === 'hortifruti') {
                headers = '<tr><th>Código</th><th>Nome do Produto</th><th>Pituba</th><th>Vitória</th><th>Vilas</th><th>Apipema</th></tr>';
            } else {
                headers = '<tr><th>Linha</th><th>Dados</th></tr>';
            }
            
            thead.innerHTML = headers;
            
            // Preencher dados da tabela
            const tbody = document.getElementById('planilhaTableBody');
            tbody.innerHTML = data.produtos.map((produto, index) => {
                if (data.tipo_processamento === 'pituba') {
                    return `<tr>
                        <td><strong>${produto.codigo}</strong></td>
                        <td>${produto.nome}</td>
                        <td>${produto.quantidade.toLocaleString('pt-BR')}</td>
                        <td>${produto.loja_destino}</td>
                    </tr>`;
                } else if (data.tipo_processamento === 'hortifruti') {
                    return `<tr>
                        <td><strong>${produto.codigo}</strong></td>
                        <td>${produto.nome}</td>
                        <td>${produto.quantidades.pituba || 0}</td>
                        <td>${produto.quantidades.vitoria || 0}</td>
                        <td>${produto.quantidades.vilas || 0}</td>
                        <td>${produto.quantidades.apipema || 0}</td>
                    </tr>`;
                } else {
                    return `<tr>
                        <td>${produto.linha}</td>
                        <td><code>${JSON.stringify(produto.dados)}</code></td>
                    </tr>`;
                }
            }).join('');
            
            document.getElementById('planilhaContent').style.display = 'block';
            console.log('Modal preenchido com sucesso');
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            document.getElementById('planilhaLoading').style.display = 'none';
            document.getElementById('planilhaError').style.display = 'block';
            document.getElementById('planilhaErrorMessage').textContent = 'Erro ao carregar dados da planilha.';
        });
}

// Visualizar TXT
function visualizarTxt(txtId) {
    console.log('Iniciando visualização do TXT:', txtId);
    abrirModal('txtModal');
    
    // Mostrar loading
    document.getElementById('txtLoading').style.display = 'block';
    document.getElementById('txtContent').style.display = 'none';
    document.getElementById('txtError').style.display = 'none';
    
    fetch(`/visualizar_txt/${txtId}`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Dados recebidos:', data);
            document.getElementById('txtLoading').style.display = 'none';
            
            if (data.error) {
                console.error('Erro retornado:', data.error);
                document.getElementById('txtError').style.display = 'block';
                document.getElementById('txtErrorMessage').textContent = data.error;
                return;
            }
            
            // Preencher informações do arquivo
            document.getElementById('txtNome').textContent = data.nome_arquivo;
            document.getElementById('txtLoja').textContent = data.tipo_loja;
            document.getElementById('txtTotalLinhas').textContent = data.total_produtos;
            
            // Preencher dados da tabela
            const tbody = document.getElementById('txtTableBody');
            tbody.innerHTML = data.produtos.map((produto, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${produto.codigo}</strong></td>
                    <td>${produto.quantidade}</td>
                    <td><code>${produto.linha_completa}</code></td>
                </tr>
            `).join('');
            
            document.getElementById('txtContent').style.display = 'block';
            console.log('Modal preenchido com sucesso');
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            document.getElementById('txtLoading').style.display = 'none';
            document.getElementById('txtError').style.display = 'block';
            document.getElementById('txtErrorMessage').textContent = 'Erro ao carregar dados do arquivo TXT.';
        });
} 