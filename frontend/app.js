/**
 * Aplicación JavaScript para el buscador de establecimientos
 * Maneja la interacción con la API y la interfaz de usuario
 */

class BuscadorEstablecimientos {
    constructor() {
        this.apiBaseUrl = 'https://maquinastabaco.onrender.com';
        this.currentSkip = 0;
        this.currentLimit = 25;
        this.currentSearch = '';
        this.currentProvincia = '';
        this.isLoading = false;
        this.hasMoreResults = false;
        this.searchTimeout = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadInitialData();
    }

    initializeElements() {
        // Elementos del DOM
        this.searchInput = document.getElementById('searchInput');
        this.provinciaSelect = document.getElementById('provinciaSelect');
        this.listaResultados = document.getElementById('listaResultados');
        this.btnCargarMas = document.getElementById('btnCargarMas');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.resultsTitle = document.getElementById('resultsTitle');
        this.resultsCount = document.getElementById('resultsCount');
    }

    bindEvents() {
        // Event listener para búsqueda con debounce
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        // Event listener para cambio de provincia
        this.provinciaSelect.addEventListener('change', (e) => {
            this.handleProvinciaChange(e.target.value);
        });

        // Event listener para botón "Cargar más"
        this.btnCargarMas.addEventListener('click', () => {
            this.loadMoreResults();
        });

        // Event listener para Enter en el input de búsqueda
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.performSearch();
            }
        });
    }

    async loadInitialData() {
        try {
            // Cargar provincias disponibles
            await this.loadProvincias();
            
            // Cargar primeros resultados
            await this.performSearch();
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            this.showError('Error al cargar los datos iniciales');
        }
    }

    async loadProvincias() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/provincias`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.populateProvinciasSelect(data.provincias);
        } catch (error) {
            console.error('Error cargando provincias:', error);
            // No mostrar error al usuario, simplemente continuar sin filtro de provincia
        }
    }

    populateProvinciasSelect(provincias) {
        // Limpiar opciones existentes excepto la primera
        while (this.provinciaSelect.children.length > 1) {
            this.provinciaSelect.removeChild(this.provinciaSelect.lastChild);
        }

        // Agregar provincias
        provincias.forEach(provincia => {
            const option = document.createElement('option');
            option.value = provincia;
            option.textContent = provincia;
            this.provinciaSelect.appendChild(option);
        });
    }

    handleSearchInput(value) {
        // Limpiar timeout anterior
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        // Establecer nuevo timeout para debounce
        this.searchTimeout = setTimeout(() => {
            this.currentSearch = value.trim();
            this.resetPagination();
            this.performSearch();
        }, 300);
    }

    handleProvinciaChange(value) {
        this.currentProvincia = value;
        this.resetPagination();
        this.performSearch();
    }

    resetPagination() {
        this.currentSkip = 0;
        this.hasMoreResults = false;
        this.btnCargarMas.style.display = 'none';
    }

    async performSearch(append = false) {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading(append);

        try {
            const params = new URLSearchParams({
                skip: this.currentSkip.toString(),
                limit: this.currentLimit.toString()
            });

            if (this.currentSearch) {
                params.append('search', this.currentSearch);
            }

            if (this.currentProvincia) {
                params.append('provincia', this.currentProvincia);
            }

            const response = await fetch(`${this.apiBaseUrl}/establecimientos?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.handleSearchResults(data, append);

        } catch (error) {
            console.error('Error en la búsqueda:', error);
            this.showError('Error al realizar la búsqueda. Por favor, inténtalo de nuevo.');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    handleSearchResults(data, append) {
        const { establecimientos, pagination } = data;

        if (!append) {
            this.listaResultados.innerHTML = '';
        }

        if (establecimientos.length === 0 && !append) {
            this.showEmptyState();
            return;
        }

        // Renderizar establecimientos
        establecimientos.forEach(establecimiento => {
            this.renderEstablecimiento(establecimiento);
        });

        // Actualizar metadatos
        this.updateResultsMetadata(pagination);

        // Mostrar/ocultar botón "Cargar más"
        this.hasMoreResults = pagination.has_more;
        this.btnCargarMas.style.display = this.hasMoreResults ? 'block' : 'none';

        // Actualizar skip para próxima carga
        this.currentSkip = pagination.next_skip || this.currentSkip + this.currentLimit;
    }

    renderEstablecimiento(establecimiento) {
        const card = document.createElement('div');
        card.className = 'establecimiento-card';
        card.innerHTML = `
            <div class="establecimiento-nombre">${this.escapeHtml(establecimiento.nombre)}</div>
            <div class="establecimiento-direccion">${this.escapeHtml(establecimiento.direccion || 'Dirección no disponible')}</div>
            <div class="establecimiento-ubicacion">
                ${this.escapeHtml(establecimiento.localidad || 'Localidad no disponible')}, 
                ${this.escapeHtml(establecimiento.provincia || 'Provincia no disponible')}
            </div>
        `;

        // Agregar animación de entrada
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        this.listaResultados.appendChild(card);

        // Animar entrada
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 50);
    }

    updateResultsMetadata(pagination) {
        const total = pagination.total;
        const returned = pagination.returned;
        const skip = pagination.skip;

        // Actualizar título
        if (this.currentSearch || this.currentProvincia) {
            let titleText = 'Resultados de búsqueda';
            if (this.currentSearch && this.currentProvincia) {
                titleText = `Resultados para "${this.currentSearch}" en ${this.currentProvincia}`;
            } else if (this.currentSearch) {
                titleText = `Resultados para "${this.currentSearch}"`;
            } else if (this.currentProvincia) {
                titleText = `Establecimientos en ${this.currentProvincia}`;
            }
            this.resultsTitle.textContent = titleText;
        } else {
            this.resultsTitle.textContent = 'Establecimientos encontrados';
        }

        // Actualizar contador
        if (total > 0) {
            const showing = skip + returned;
            this.resultsCount.textContent = `Mostrando ${showing} de ${total}`;
            this.resultsCount.style.display = 'block';
        } else {
            this.resultsCount.style.display = 'none';
        }
    }

    async loadMoreResults() {
        if (this.hasMoreResults && !this.isLoading) {
            await this.performSearch(true);
        }
    }

    showLoading(append = false) {
        if (!append) {
            this.loadingIndicator.style.display = 'flex';
        }
    }

    hideLoading() {
        this.loadingIndicator.style.display = 'none';
    }

    showEmptyState() {
        this.listaResultados.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No se encontraron resultados</h3>
                <p>
                    ${this.currentSearch || this.currentProvincia 
                        ? 'Intenta modificar tu búsqueda o cambiar el filtro de provincia.' 
                        : 'No hay establecimientos disponibles en este momento.'}
                </p>
            </div>
        `;
        this.resultsCount.style.display = 'none';
    }

    showError(message) {
        this.listaResultados.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
        this.resultsCount.style.display = 'none';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new BuscadorEstablecimientos();
});

// Manejar errores globales de fetch
window.addEventListener('unhandledrejection', (event) => {
    console.error('Error no manejado:', event.reason);
    // Opcional: mostrar notificación al usuario
});

// Funciones de utilidad adicionales
const utils = {
    // Función para formatear números
    formatNumber: (num) => {
        return new Intl.NumberFormat('es-ES').format(num);
    },

    // Función para capitalizar texto
    capitalize: (str) => {
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    },

    // Función para truncar texto
    truncate: (str, length = 100) => {
        if (str.length <= length) return str;
        return str.substring(0, length) + '...';
    }
};
