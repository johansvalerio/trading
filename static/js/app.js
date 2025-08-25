
let currentGraph = null;

// Función para formatear números
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// Función para formatear fechas
function formatTime(dateString, includeSeconds = false) {
    if (!dateString) return '--';

    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString; // Si no es una fecha válida, devolver el string original

        const options = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: includeSeconds ? '2-digit' : undefined,
            hour12: true,
        };

        return date.toLocaleString('es-ES', options).replace(',', '');
    } catch (e) {
        console.error('Error al formatear fecha:', e);
        return dateString;
    }
}

// Inicializar valores por defecto al cargar la página
function initializeDefaultValues() {
    // Inicializar análisis de volumen con valores por defecto
    const volumeValueEl = document.getElementById('volume-ratio-value');
    const volumeBarEl = document.getElementById('volume-ratio-bar');
    if (volumeValueEl) volumeValueEl.textContent = '1.00x promedio (0 / 0)';
    if (volumeBarEl) {
        volumeBarEl.style.width = '50%';
        volumeBarEl.className = 'progress-bar bg-success';
    }

    // Inicializar gestión de riesgo con valores por defecto
    const riskRatioEl = document.getElementById('risk-reward-ratio');
    const positionSizeEl = document.getElementById('position-size');
    const tradeRiskEl = document.getElementById('trade-risk');
    if (riskRatioEl) riskRatioEl.textContent = '2.00';
    if (positionSizeEl) positionSizeEl.textContent = '0.0100 BTC';
    if (tradeRiskEl) tradeRiskEl.textContent = '1.00%';

    // Inicializar RSI con valores por defecto
    const rsiBar = document.getElementById('rsi-bar');
    const rsiValue = document.getElementById('rsi-value');
    if (rsiBar) {
        rsiBar.style.width = '50%';
        rsiBar.className = 'progress-bar bg-warning';
    }
    if (rsiValue) rsiValue.textContent = '50.00';

    // Inicializar valores de predicción IA
    const aiPredictionValue = document.getElementById('ai-prediction-value');
    const aiPredictionAction = document.getElementById('ai-prediction-action');
    const aiConfidenceBar = document.getElementById('ai-confidence-bar');
    const aiConfidenceBadge = document.getElementById('ai-confidence-badge');
    const aiActionText = document.getElementById('ai-action-text');
    const aiActionReason = document.getElementById('ai-action-reason');
    const aiRecommendation = document.getElementById('ai-recommendation');

    if (aiPredictionValue) aiPredictionValue.textContent = 'Analizando...';
    if (aiPredictionAction) aiPredictionAction.textContent = 'Analizando...';
    if (aiConfidenceBar) {
        aiConfidenceBar.style.width = '0%';
        aiConfidenceBar.className = 'progress-bar bg-danger';
        aiConfidenceBar.setAttribute('aria-valuenow', '0');
    }
    if (aiConfidenceBadge) {
        aiConfidenceBadge.textContent = 'Confianza: 0.0%';
        aiConfidenceBadge.className = 'badge bg-danger';
    }
    if (aiActionText) aiActionText.textContent = 'Esperar';
    if (aiActionReason) aiActionReason.textContent = 'Esperando datos de la IA...';
    if (aiRecommendation) {
        aiRecommendation.className = 'alert text-center mb-0 alert-secondary';
        aiRecommendation.style.display = 'block';
    }

    // Inicializar otros valores
    const trendStatusEl = document.getElementById('trend-status-value');
    const marketBadgeEl = document.getElementById('market-trend-badge');
    if (trendStatusEl) trendStatusEl.textContent = 'Analizando...';
    if (marketBadgeEl) {
        marketBadgeEl.textContent = 'Cargando...';
        marketBadgeEl.className = 'badge bg-secondary';
    }
}

// Función para actualizar los datos
async function updateData() {
    try {
        console.log('Solicitando datos...');
        const response = await fetch('/api/data');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error en la respuesta del servidor');
        }

        console.log('Datos recibidos:', data);

        // Actualizar el gráfico si hay datos
        if (data.graph && data.graph.data && data.graph.data.length > 0) {
            console.log('Actualizando gráfico con datos:', data.graph);
            try {
                // Asegurarse de que las fechas estén en el formato correcto
                if (data.graph.data[0].x && data.graph.data[0].x.length > 0) {
                    // Configuración del tema oscuro
                    const darkTheme = {
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#e0e0e0' },
                        xaxis: {
                            gridcolor: 'rgba(255, 255, 255, 0.1)',
                            linecolor: 'rgba(255, 255, 255, 0.2)',
                            zerolinecolor: 'rgba(255, 255, 255, 0.1)',
                            showgrid: true,
                            rangeslider: { visible: true },
                            type: 'date'
                        },
                        yaxis: {
                            gridcolor: 'rgba(255, 255, 255, 0.1)',
                            linecolor: 'rgba(255, 255, 255, 0.2)',
                            zerolinecolor: 'rgba(255, 255, 255, 0.1)',
                            showgrid: true,
                            fixedrange: false,
                            side: 'right',
                            title: 'Precio',
                            titlefont: { color: '#e0e0e0' },
                            tickfont: { color: '#e0e0e0' },
                            tickformat: '.8f'
                        },
                        hovermode: 'x unified',
                        hoverlabel: {
                            bgcolor: 'rgba(30, 30, 30, 0.9)',
                            font: { color: '#e0e0e0' }
                        },
                        legend: {
                            orientation: 'h',
                            y: -0.2,
                            font: { color: '#e0e0e0' },
                            bgcolor: 'rgba(0, 0, 0, 0.5)'
                        },
                        margin: { t: 30, b: 50, l: 50, r: 30, pad: 4 },
                        showlegend: true,
                        dragmode: 'zoom',
                        selectdirection: 'any',
                        xaxis_rangeslider_visible: false
                    };

                    // Combinar el layout del servidor con el tema oscuro
                    const layout = {
                        ...data.graph.layout,
                        ...darkTheme,
                        template: 'plotly_dark'
                    };

                    const config = {
                        responsive: true,
                        displayModeBar: true,
                        scrollZoom: true,
                        displaylogo: false,
                        modeBarButtonsToAdd: ['select2d', 'lasso2d'],
                        modeBarButtonsToRemove: ['zoomIn', 'zoomOut', 'autoScale', 'resetScale', 'select'],
                        toImageButtonOptions: {
                            format: 'png',
                            filename: 'grafico-forex',
                            height: 600,
                            width: 1000,
                            scale: 1
                        },
                        modeBar: {
                            bgcolor: 'rgba(0, 0, 0, 0.7)',
                            color: '#e0e0e0',
                            activecolor: '#4b6cb7'
                        }
                    };

                    // Asegurar que los datos tengan colores visibles en modo oscuro
                    const updatedData = data.graph.data.map(trace => {
                        const newTrace = { ...trace };
                        if (newTrace.line) {
                            newTrace.line = {
                                ...newTrace.line,
                                color: newTrace.line.color || '#4b6cb7',
                                width: newTrace.line.width || 2
                            };
                        }
                        return newTrace;
                    });

                    Plotly.react('graph', updatedData, layout, config);
                    console.log('Gráfico actualizado correctamente');
                } else {
                    console.warn('Datos del gráfico incompletos o en formato incorrecto');
                }
            } catch (plotError) {
                console.error('Error al actualizar el gráfico:', plotError);
            }
        } else {
            console.warn('No hay datos de gráfico para mostrar');
        }

        // Datos de backend como objetos
        console.log('Datos recibidos del backend:', data);

        // Actualizar las condiciones para ambas señales
        function updateConditions(type, signalData, indicators) {
            // Usar datos de los indicadores generales si la señal no está activa
            const data = {
                rsi: indicators.rsi,
                macd: indicators.macd,
                macd_signal: indicators.macd_signal,
                sma_20: indicators.sma_20,
                sma_50: indicators.sma_50,
                sma_200: indicators.sma_200,
                adx: indicators.adx,
                di_plus: indicators.di_plus,
                di_minus: indicators.di_minus,
                volume_ratio: indicators.volume_ratio,
                score: indicators.score,
                ...signalData // Los datos de la señal sobrescribirán los indicadores si existen
            };

            const conditions = [
                {
                    id: `${type}-rsi-condition`,
                    valueId: `${type}-rsi-value`,
                    check: () => {
                        const rsiValue = data.rsi ? parseFloat(data.rsi) : null;
                        const condition = rsiValue !== null && (type === 'buy' ? rsiValue < 30 : rsiValue > 70);
                        return {
                            met: condition,
                            value: rsiValue !== null ? rsiValue.toFixed(2) : '--',
                            threshold: type === 'buy' ? '< 30' : '> 70'
                        };
                    }
                },
                {
                    id: `${type}-macd-condition`,
                    valueId: `${type}-macd-value`,
                    check: () => {
                        const macd = data.macd ? parseFloat(data.macd) : null;
                        const macdSignal = data.macd_signal ? parseFloat(data.macd_signal) : null;
                        const condition = macd !== null && macdSignal !== null &&
                            (type === 'buy' ? macd > macdSignal : macd < macdSignal);
                        return {
                            met: condition,
                            value: `${macd !== null ? macd.toFixed(6) : '--'} | ${macdSignal !== null ? macdSignal.toFixed(6) : '--'}`,
                            threshold: type === 'buy' ? 'MACD > Señal' : 'MACD < Señal'
                        };
                    }
                },
                {
                    id: `${type}-sma-condition`,
                    valueId: `${type}-sma-value`,
                    check: () => {
                        const sma20 = data.sma_20 ? parseFloat(data.sma_20) : null;
                        const sma50 = data.sma_50 ? parseFloat(data.sma_50) : null;
                        const condition = sma20 !== null && sma50 !== null &&
                            (type === 'buy' ? sma20 > sma50 : sma20 < sma50);
                        return {
                            met: condition,
                            value: `${sma20 !== null ? sma20.toFixed(2) : '--'} | ${sma50 !== null ? sma50.toFixed(2) : '--'}`,
                            threshold: type === 'buy' ? 'SMA20 > SMA50' : 'SMA20 < SMA50'
                        };
                    }
                },
                {
                    id: `${type}-adx-condition`,
                    valueId: `${type}-adx-value`,
                    check: () => {
                        const adx = data.adx ? parseFloat(data.adx) : null;
                        const condition = adx !== null && adx > 25;
                        return {
                            met: condition,
                            value: adx !== null ? adx.toFixed(2) : '--',
                            threshold: '> 25'
                        };
                    }
                },
                {
                    id: `${type}-volume-condition`,
                    valueId: `${type}-volume-value`,
                    check: () => {
                        const volumeRatio = data.volume_ratio ? parseFloat(data.volume_ratio) : null;
                        const condition = volumeRatio !== null && volumeRatio > 1;
                        return {
                            met: condition,
                            value: volumeRatio !== null ? volumeRatio.toFixed(2) : '--',
                            threshold: '> 1'
                        };
                    }
                },
                {
                    id: `${type}-score-condition`,
                    valueId: `${type}-score-value`,
                    check: () => {
                        const score = data.score ? parseFloat(data.score) : null;
                        const threshold = type === 'buy' ? 0.6 : -0.6;
                        const condition = score !== null && (type === 'buy' ? score > threshold : score < threshold);
                        return {
                            met: condition,
                            value: score !== null ? score.toFixed(2) : '--',
                            threshold: type === 'buy' ? '> 0.6' : '< -0.6'
                        };
                    }
                }
            ];

            conditions.forEach(condition => {
                const element = document.getElementById(condition.id);
                const valueElement = document.getElementById(condition.valueId);

                if (element && valueElement) {
                    const result = condition.check();
                    element.className = `condition-item ${result.met ? 'met' : 'not-met'}`;

                    // Ensure only one icon exists by removing all existing icons
                    const existingIcons = Array.from(element.children).filter(child => child.classList && child.classList.contains('condition-icon'));
                    existingIcons.forEach(icon => icon.remove());

                    // Create a new icon only if necessary
                    const icon = document.createElement('i');
                    icon.className = `condition-icon fas condition-status-icon ${result.met ? 'fa-check-circle' : 'fa-times-circle'}`;
                    icon.style.color = result.met ? '#28a745' : '#dc3545';
                    element.insertBefore(icon, element.firstChild);

                    // Update the value display
                    const valueDisplay = typeof result.value === 'number' ? result.value.toFixed(2) : result.value;
                    if (valueElement) {
                        valueElement.innerHTML = `
                <span class="current-value">${valueDisplay}</span>
                <small class="text-muted"> (Req: ${result.threshold})</small>
            `;
                    }

                    // Add a tooltip with more information
                    element.title = `Valor actual: ${valueDisplay}\nRequerido: ${result.threshold}`;

                    console.log(`${type} - ${condition.id}: ${result.met ? 'Cumplido' : 'No cumplido'}`);
                    console.log(`Valor: ${valueDisplay}, Requerido: ${result.threshold}`);
                }
            });

            // Final cleanup of any orphaned icons
            document.querySelectorAll('.condition-item i:not(.condition-icon)').forEach(icon => icon.remove());
        }

        // Limpiar cualquier ícono huérfano antes de actualizar
        document.querySelectorAll('.condition-item i:not(.condition-icon)').forEach(icon => icon.remove());

        // Actualizar condiciones para ambas señales usando tanto los datos de la señal como los indicadores
        console.log('Actualizando condiciones de compra...');
        updateConditions('buy', data.buy_signal || {}, data.indicators || {});
        console.log('Actualizando condiciones de venta...');
        updateConditions('sell', data.sell_signal || {}, data.indicators || {});                // Actualizar tarjetas de señales con información de riesgo
        updateSignalCard('buy', data.buy_signal.active, data.buy_signal, data.last_price, data.stop_loss_info);
        updateSignalCard('sell', data.sell_signal.active, data.sell_signal, data.last_price, data.stop_loss_info);

        const buy = data.buy_signal || { active: false };
        const sell = data.sell_signal || { active: false };

        // Actualizar indicadores técnicos
        if (data.indicators) {
            const indicators = data.indicators;

            // Actualizar valores de los indicadores
            document.getElementById('macd-value').textContent = indicators.macd ? indicators.macd.toFixed(4) : '-';
            document.getElementById('macd-signal-value').textContent = indicators.macd_signal ? indicators.macd_signal.toFixed(4) : '-';
            document.getElementById('adx-value').textContent = indicators.adx ? indicators.adx.toFixed(2) : '-';
            document.getElementById('atr-value').textContent = indicators.atr ? indicators.atr.toFixed(4) : '-';

            // Actualizar barras de progreso
            const adxBar = document.getElementById('adx-bar');
            const atrBar = document.getElementById('atr-bar');
            if (adxBar) {
                const adxPercent = Math.min(100, (indicators.adx || 0) * 2);
                adxBar.style.width = `${adxPercent}%`;
                adxBar.className = `progress-bar ${indicators.adx > 25 ? 'bg-success' : 'bg-warning'}`;
            }
            if (atrBar) {
                // Normalizar ATR para la barra de progreso (ajustar según sea necesario)
                const atrPercent = Math.min(100, (indicators.atr || 0) * 10);
                atrBar.style.width = `${atrPercent}%`;
            }

            // Actualizar predicción de IA
            const aiPredictionEl = document.getElementById('ai-prediction-value');
            const aiConfidenceBadge = document.getElementById('ai-confidence-badge');
            if (indicators.ai_prediction) {
                const prediction = indicators.ai_prediction;
                const isBullish = prediction.prediction && prediction.prediction.toLowerCase().includes('compra');

                if (aiPredictionEl) {
                    aiPredictionEl.textContent = prediction.prediction || '-';
                    aiPredictionEl.className = `metric-value ${isBullish ? 'text-success' : 'text-danger'}`;
                }

                if (aiConfidenceBadge) {
                    const confidence = Math.min(Math.max(prediction.confidence * 100, 0), 100).toFixed(1);
                    aiConfidenceBadge.textContent = `Confianza: ${confidence}%`;
                    aiConfidenceBadge.className = `badge ${isBullish ? 'bg-success' : 'bg-danger'}`;
                }
            }

            // Actualizar estado del mercado
            const trendStatusEl = document.getElementById('trend-status-value');
            const marketTrendBadge = document.getElementById('market-trend-badge');
            if (trendStatusEl && marketTrendBadge) {
                const trend = indicators.trend_strength || 'Neutral';
                trendStatusEl.textContent = trend;

                // Actualizar el color del badge según la tendencia
                if (trend.toLowerCase().includes('alcista')) {
                    marketTrendBadge.className = 'badge bg-success';
                    marketTrendBadge.textContent = 'Alcista';
                } else if (trend.toLowerCase().includes('bajista')) {
                    marketTrendBadge.className = 'badge bg-danger';
                    marketTrendBadge.textContent = 'Bajista';
                } else {
                    marketTrendBadge.className = 'badge bg-secondary';
                    marketTrendBadge.textContent = 'Neutral';
                }
            }
        }

        console.log('Señal de compra:', buy);
        console.log('Señal de venta:', sell);
        console.log('buy.active:', buy.active, 'sell.active:', sell.active);

        // Obtener referencias a los elementos del DOM
        const buyPrice = document.getElementById('buy-price');
        const buyRsi = document.getElementById('buy-rsi');
        const buyMacd = document.getElementById('buy-macd');
        const buySigNum = document.getElementById('buy-signal-num');
        const buyTime = document.getElementById('buy-time');
        const buyCard = document.getElementById('buy-signal');

        const sellPrice = document.getElementById('sell-price');
        const sellRsi = document.getElementById('sell-rsi');
        const sellMacd = document.getElementById('sell-macd');
        const sellSigNum = document.getElementById('sell-signal-num');
        const sellTime = document.getElementById('sell-time');
        const sellCard = document.getElementById('sell-signal');

        const lastPriceEl = document.getElementById('last-price');

        // Actualizar tarjeta de compra
        if (buyCard) {
            // Actualizar los valores de la tarjeta de compra
            const price = isFinite(buy.price) && buy.price > 0 ?
                `<i class="fas fa-dollar-sign text-success me-1"></i><strong>${formatNumber(buy.price, 2)}</strong>` : '--';

            const rsiValue = isFinite(buy.rsi) && buy.rsi > 0 ? parseFloat(buy.rsi) : null;
            let rsiHtml = '--';
            if (rsiValue !== null) {
                const rsiClass = rsiValue < 30 ? 'text-success' : rsiValue > 70 ? 'text-danger' : 'text-warning';
                rsiHtml = `<i class="fas fa-arrow-trend-up ${rsiClass} me-1"></i><span class="${rsiClass}">${formatNumber(rsiValue, 2)}</span>`;
            }

            const macdValue = isFinite(buy.macd) ? parseFloat(buy.macd) : null;
            let macdHtml = '--';
            if (macdValue !== null) {
                const macdSignal = isFinite(buy.macd_signal) ? parseFloat(buy.macd_signal) : null;
                const macdClass = macdSignal !== null ? (macdValue > macdSignal ? 'text-success' : 'text-danger') : 'text-primary';
                macdHtml = `<i class="fas fa-wave-square ${macdClass} me-1"></i><span class="${macdClass}">${formatNumber(macdValue, 5)}</span>`;
                if (macdSignal !== null) {
                    macdHtml += `<br><small class="text-muted">Señal: ${formatNumber(macdSignal, 5)}</small>`;
                }
            }

            const signalId = (buy && (Number.isFinite(buy.id) || typeof buy.id === 'number') && buy.id > 0) ? String(buy.id) : '--';

            const timeValue = buy.time_iso ? formatTime(buy.time_iso) : '--';
            const timeHtml = `<i class="far fa-calendar-alt text-info me-1"></i>${timeValue}`;

            // Actualizar el DOM
            if (buyPrice) buyPrice.innerHTML = price;
            if (buyRsi) buyRsi.innerHTML = rsiHtml;
            if (buyMacd) buyMacd.innerHTML = macdHtml;
            if (buySigNum) buySigNum.textContent = signalId;
            if (buyTime) buyTime.innerHTML = timeHtml;

            // Activar/desactivar tarjeta basado en la señal
            if (buy.active) {
                buyCard.classList.add('active');
                console.log('Activando señal de COMPRA');
            } else {
                buyCard.classList.remove('active');
            }
        }

        if (sellCard) {
            // Actualizar los valores de la tarjeta de venta
            const price = isFinite(sell.price) && sell.price > 0 ?
                `<i class="fas fa-dollar-sign text-danger me-1"></i>${formatNumber(sell.price, 2)}` : '--';

            const rsiValue = isFinite(sell.rsi) && sell.rsi > 0 ? formatNumber(sell.rsi, 2) : '--';
            const rsiHtml = `<i class="fas fa-arrow-trend-down text-warning me-1"></i>${rsiValue}`;

            const macdValue = isFinite(sell.macd) ? formatNumber(sell.macd, 5) : '--';
            const macdHtml = `<i class="fas fa-wave-square text-primary me-1"></i>${macdValue}`;

            const signalId = (sell && (Number.isFinite(sell.id) || typeof sell.id === 'number') && sell.id > 0) ? String(sell.id) : '--';

            const timeValue = sell.time_iso ? formatTime(sell.time_iso) : '--';
            const timeHtml = `<i class="far fa-calendar-alt text-info me-1"></i>${timeValue}`;

            // Actualizar el DOM
            if (sellPrice) sellPrice.innerHTML = price;
            if (sellRsi) sellRsi.innerHTML = rsiHtml;
            if (sellMacd) sellMacd.innerHTML = macdHtml;
            if (sellSigNum) sellSigNum.textContent = signalId;
            if (sellTime) sellTime.innerHTML = timeHtml;

            // Activar/desactivar tarjeta basado en la señal
            if (sell.active) {
                sellCard.classList.add('active');
                console.log('Activando señal de VENTA');
            } else {
                sellCard.classList.remove('active');
            }
        }

        // Actualizar precio USDT (último)
        if (lastPriceEl && isFinite(data.last_price)) {
            lastPriceEl.textContent = formatNumber(data.last_price, 2);
        }

        // Añadir manejadores de clic para actualizar los datos
        if (buyCard && !buyCard._boundClick) {
            buyCard.addEventListener('click', updateData);
            buyCard._boundClick = true;
        }

        if (sellCard && !sellCard._boundClick) {
            sellCard.addEventListener('click', updateData);
            sellCard._boundClick = true;
        }

        // Actualizar recomendaciones
        if (typeof updateRecommendations === 'function') {
            updateRecommendations(data);
        }

        // Actualizar marca de tiempo
        const lastUpdateEl = document.getElementById('last-update');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = `Última actualización: ${new Date().toLocaleTimeString()}`;
        }

        // Actualizar MACD y su interpretación
        const macdValue = data.macd ? parseFloat(data.macd) : 0;
        const macdSignalValue = data.macd_signal ? parseFloat(data.macd_signal) : 0;
        $('#macd-value').text(macdValue.toFixed(6));
        $('#macd-signal-value').text(macdSignalValue.toFixed(6));

        // Interpretar MACD
        const macdStatus = document.getElementById('macd-status');
        const macdInterpretation = document.getElementById('macd-interpretation');
        if (macdValue > macdSignalValue) {
            macdStatus.className = 'alert alert-success mb-0';
            macdInterpretation.textContent = 'Señal alcista: MACD por encima de la línea de señal';
        } else if (macdValue < macdSignalValue) {
            macdStatus.className = 'alert alert-danger mb-0';
            macdInterpretation.textContent = 'Señal bajista: MACD por debajo de la línea de señal';
        } else {
            macdStatus.className = 'alert alert-warning mb-0';
            macdInterpretation.textContent = 'Cruce potencial: MACD cerca de la línea de señal';
        }

        // Actualizar ADX y su interpretación
        const adxValue = data.adx ? parseFloat(data.adx) : 0;
        $('#adx-value').text(adxValue.toFixed(2));
        const adxPercent = Math.min(100, (adxValue / 50) * 100);
        const adxBar = $('#adx-bar');
        adxBar.css('width', adxPercent + '%');

        // Ajustar color de la barra ADX según el nivel
        if (adxValue >= 50) {
            adxBar.removeClass('bg-warning bg-danger').addClass('bg-success');
        } else if (adxValue >= 25) {
            adxBar.removeClass('bg-success bg-danger').addClass('bg-warning');
        } else {
            adxBar.removeClass('bg-success bg-warning').addClass('bg-danger');
        }

        // Interpretar ADX
        const adxStatus = document.getElementById('adx-status');
        const adxInterpretation = document.getElementById('adx-interpretation');
        if (adxValue >= 50) {
            adxStatus.className = 'alert alert-success mb-0';
            adxInterpretation.textContent = 'Tendencia muy fuerte - Buenas condiciones para trading';
        } else if (adxValue >= 25) {
            adxStatus.className = 'alert alert-warning mb-0';
            adxInterpretation.textContent = 'Tendencia moderada - Considerar operaciones con precaución';
        } else {
            adxStatus.className = 'alert alert-danger mb-0';
            adxInterpretation.textContent = 'Tendencia débil - Mercado lateral, trading riesgoso';
        }

        // Actualizar ATR y su interpretación
        const atrValue = data.atr ? parseFloat(data.atr) : 0;
        $('#atr-value').text(atrValue.toFixed(6));

        // Calcular ATR relativo (como porcentaje del precio)
        const currentPrice = parseFloat(data.last_price) || 1;
        const atrPercent = (atrValue / currentPrice) * 100;
        const atrBar = $('#atr-bar');
        const normalizedAtrPercent = Math.min(100, atrPercent * 20); // Multiplicar por 20 para mejor visualización
        atrBar.css('width', normalizedAtrPercent + '%');

        // Ajustar color de la barra ATR
        if (atrPercent < 0.5) {
            atrBar.removeClass('bg-warning bg-danger').addClass('bg-success');
        } else if (atrPercent < 1) {
            atrBar.removeClass('bg-success bg-danger').addClass('bg-warning');
        } else {
            atrBar.removeClass('bg-success bg-warning').addClass('bg-danger');
        }

        // Interpretar ATR
        const atrStatus = document.getElementById('atr-status');
        const atrInterpretation = document.getElementById('atr-interpretation');
        if (atrPercent < 0.5) {
            atrStatus.className = 'alert alert-success mb-0';
            atrInterpretation.textContent = 'Volatilidad baja - Condiciones estables para trading';
        } else if (atrPercent < 1) {
            atrStatus.className = 'alert alert-warning mb-0';
            atrInterpretation.textContent = 'Volatilidad moderada - Ajustar stop loss según corresponda';
        } else {
            atrStatus.className = 'alert alert-danger mb-0';
            atrInterpretation.textContent = 'Volatilidad alta - Precaución, mayor riesgo';
        }

        // Actualizar RSI y su interpretación
        const rsiValue = data.rsi ? parseFloat(data.rsi) : 0;
        $('#rsi-value').text(rsiValue.toFixed(2));

        // Actualizar barra de progreso RSI
        const rsiBar = $('#rsi-bar');
        rsiBar.css('width', rsiValue + '%');

        // Ajustar color de la barra RSI
        if (rsiValue <= 30) {
            rsiBar.removeClass('bg-warning bg-success').addClass('bg-danger');
        } else if (rsiValue >= 70) {
            rsiBar.removeClass('bg-warning bg-danger').addClass('bg-success');
        } else {
            rsiBar.removeClass('bg-success bg-danger').addClass('bg-warning');
        }

        // Interpretar RSI
        const rsiStatus = document.getElementById('rsi-status');
        const rsiInterpretation = document.getElementById('rsi-interpretation');
        if (rsiValue <= 30) {
            rsiStatus.className = 'alert alert-danger mb-0';
            rsiInterpretation.textContent = 'Sobrevendido - Posible oportunidad de compra';
        } else if (rsiValue >= 70) {
            rsiStatus.className = 'alert alert-success mb-0';
            rsiInterpretation.textContent = 'Sobrecomprado - Posible oportunidad de venta';
        } else {
            rsiStatus.className = 'alert alert-warning mb-0';
            rsiInterpretation.textContent = 'Neutral - Mercado en equilibrio';
        }

        // Actualizar Contexto de Mercado
        if (data.market_context) {
            const context = data.market_context;

            // Actualizar indicadores de mercado
            const sidewaysBadge = document.getElementById('sideways-market-badge');
            const sentimentBadge = document.getElementById('sentiment-badge');
            const volatilityBadge = document.getElementById('volatility-badge');
            const crisisBadge = document.getElementById('crisis-badge');

            // Mercado lateral
            if (sidewaysBadge) {
                sidewaysBadge.textContent = context.is_sideways ? 'Lateral' : 'Tendencial';
                sidewaysBadge.className = `badge ${context.is_sideways ? 'bg-warning' : 'bg-success'}`;
            }

            // Sentimiento
            if (sentimentBadge) {
                sentimentBadge.textContent = context.sentiment;
                sentimentBadge.className = `badge ${context.sentiment === 'Positivo' ? 'bg-success' :
                    context.sentiment === 'Negativo' ? 'bg-danger' : 'bg-warning'}`;
            }

            // Volatilidad
            if (volatilityBadge) {
                volatilityBadge.textContent = context.volatility;
                volatilityBadge.className = `badge ${context.volatility === 'Alta' ? 'bg-danger' :
                    context.volatility === 'Media' ? 'bg-warning' : 'bg-success'}`;
            }

            // Crisis
            if (crisisBadge) {
                crisisBadge.textContent = context.crisis_detected ? 'CRISIS' : 'Normal';
                crisisBadge.className = `badge ${context.crisis_detected ? 'bg-danger' : 'bg-success'}`;
            }

            // Actualizar razones bloqueadas
            const blockedReasonsList = document.getElementById('blocked-reasons-list');
            if (blockedReasonsList) {
                blockedReasonsList.innerHTML = '';
                if (context.skip_reasons && context.skip_reasons.length > 0) {
                    context.skip_reasons.forEach(reason => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item text-danger';
                        li.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${reason}`;
                        blockedReasonsList.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.className = 'list-group-item text-success';
                    li.innerHTML = '<i class="fas fa-check-circle me-2"></i>Condiciones óptimas para trading';
                    blockedReasonsList.appendChild(li);
                }
            }
        }

        // Actualizar predicción IA y métricas relacionadas
        const aiPrediction = data.ai_prediction;
        const predictionText = aiPrediction === 1 ?
            '<span class="text-success"><i class="fas fa-arrow-up"></i> Alcista</span>' :
            '<span class="text-danger"><i class="fas fa-arrow-down"></i> Bajista</span>';
        $('#ai-prediction-value').html(predictionText);

        // Actualizar barra y badge de confianza
        if (data.indicators && data.indicators.ai_prediction) {
            const confidence = Math.min(Math.max(data.indicators.ai_prediction.confidence * 100, 0), 100);
            $('#ai-confidence-bar').css('width', `${confidence}%`)
                .removeClass('bg-success bg-warning bg-danger')
                .addClass(confidence > 70 ? 'bg-success' : confidence > 40 ? 'bg-warning' : 'bg-danger')
                .attr('aria-valuenow', confidence)
                .attr('title', `Confianza: ${confidence.toFixed(1)}%`);
            $('#ai-confidence-badge').text(`Confianza: ${confidence.toFixed(1)}%`);

            // Actualizar métricas de precisión si están disponibles
            if (data.indicators.ai_prediction.accuracy) {
                $('#ai-accuracy').text(`${(data.indicators.ai_prediction.accuracy * 100).toFixed(1)}%`);
            }
            if (data.indicators.ai_prediction.success_rate) {
                $('#ai-success-rate').text(`${(data.indicators.ai_prediction.success_rate * 100).toFixed(1)}%`);
            }
        }

        // Actualizar gestión de riesgo - SIEMPRE mostrar datos calculados
        if (data.indicators && data.indicators.risk_management) {
            const riskInfo = data.indicators.risk_management;

            // Actualizar valores con datos calculados del mercado
            const riskRatioEl = document.getElementById('risk-reward-ratio');
            if (riskRatioEl) {
                riskRatioEl.textContent = riskInfo.risk_reward_ratio ? `${riskInfo.risk_reward_ratio.toFixed(2)}` : '2.00';
            }

            // Calcular tamaño de posición basado en riesgo estándar
            const currentPrice = parseFloat(data.last_price) || 0;
            const riskAmount = 10000 * 0.01; // 1% de 10000 USDT
            const stopLossDistance = 0.02 * currentPrice; // 2% de distancia al SL
            const positionSize = currentPrice > 0 ? (riskAmount / stopLossDistance).toFixed(4) : '0.0000';

            const positionSizeEl = document.getElementById('position-size');
            if (positionSizeEl) positionSizeEl.textContent = `${positionSize} BTC`;

            const tradeRiskEl = document.getElementById('trade-risk');
            if (tradeRiskEl) tradeRiskEl.textContent = riskInfo.trade_risk ? `${riskInfo.trade_risk.toFixed(2)}%` : '1.00%';
        } else {
            // Mostrar valores por defecto si no hay datos
            const riskRatioEl = document.getElementById('risk-reward-ratio');
            const positionSizeEl = document.getElementById('position-size');
            const tradeRiskEl = document.getElementById('trade-risk');

            if (riskRatioEl) {
                riskRatioEl.textContent = '2.00';
            }
            if (positionSizeEl) positionSizeEl.textContent = '0.0100 BTC';
            if (tradeRiskEl) tradeRiskEl.textContent = '1.00%';
        }

        // Actualizar análisis de volumen - SIEMPRE mostrar datos calculados
        if (data.indicators && data.indicators.volume_analysis) {
            const volumeInfo = data.indicators.volume_analysis;
            const volumeRatio = volumeInfo.ratio || 1.0;
            const currentVolume = volumeInfo.current_volume || 0;
            const averageVolume = volumeInfo.average_volume || 0;

            // Actualizar barra de volumen siempre
            const ratioPercentage = Math.min(volumeRatio * 50, 100); // Normalizar para visualización
            const volumeBar = document.getElementById('volume-ratio-bar');
            if (volumeBar) {
                volumeBar.style.width = `${ratioPercentage}%`;

                // Actualizar color según el ratio
                volumeBar.className = 'progress-bar';
                if (volumeRatio > 2.0) {
                    volumeBar.classList.add('bg-danger');
                } else if (volumeRatio > 1.5) {
                    volumeBar.classList.add('bg-warning');
                } else {
                    volumeBar.classList.add('bg-success');
                }
            }

            // Actualizar texto del valor
            const volumeValueEl = document.getElementById('volume-ratio-value');
            if (volumeValueEl) {
                volumeValueEl.textContent = `${volumeRatio.toFixed(2)}x promedio (${formatNumber(currentVolume, 0)} / ${formatNumber(averageVolume, 0)})`;
            }

            // Manejar alerta de volumen
            const volumeAlert = document.getElementById('volume-alert');
            if (volumeAlert) {
                if (volumeInfo.alert || volumeRatio > 2.0) {
                    volumeAlert.style.display = 'block';
                    volumeAlert.innerHTML = `
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                Volumen anormal: ${volumeRatio.toFixed(1)}x el promedio (${formatNumber(currentVolume, 0)} vs ${formatNumber(averageVolume, 0)})
                            `;
                    volumeAlert.className = `alert p-2 mb-0 ${volumeRatio > 3 ? 'alert-danger' : 'alert-warning'}`;
                } else {
                    volumeAlert.style.display = 'none';
                }
            }
        } else {
            // Mostrar valores por defecto si no hay datos
            const volumeBar = document.getElementById('volume-ratio-bar');
            const volumeValueEl = document.getElementById('volume-ratio-value');
            const volumeAlert = document.getElementById('volume-alert');

            if (volumeBar) {
                volumeBar.style.width = '50%';
                volumeBar.className = 'progress-bar bg-success';
            }
            if (volumeValueEl) volumeValueEl.textContent = '1.00x promedio';
            if (volumeAlert) volumeAlert.style.display = 'none';
        }                    // Actualizar estado de la tendencia
        const trendStatusEl = document.getElementById('trend-status-value');
        if (trendStatusEl) trendStatusEl.textContent = data.trend_status || 'Indeterminado';

        // Actualizar badges de información adicional
        const trendBadge = document.getElementById('market-trend-badge');
        if (trendBadge) {
            if (data.trend_status === 'Fuerte') {
                trendBadge.className = 'badge bg-success';
                trendBadge.textContent = 'Tendencia Fuerte';
            } else if (data.trend_status === 'Lateral') {
                trendBadge.className = 'badge bg-warning text-dark';
                trendBadge.textContent = 'Mercado Lateral';
            } else {
                trendBadge.className = 'badge bg-secondary';
                trendBadge.textContent = 'Indeterminado';
            }
        }



    } catch (error) {
        console.error('Error al actualizar datos:', error);
    }
}

// Función para actualizar las tarjetas de señales con información de riesgo
function updateSignalCard(type, isActive, signalData, currentPrice, stopLossInfo) {
    const signalCard = document.getElementById(`${type}-signal`);
    const statusBadge = signalCard.querySelector('.status-text');
    const riskInfo = signalCard.querySelector('.risk-info');

    if (!isActive || !signalData) {
        // Ocultar sección de riesgo si no hay señal activa
        if (riskInfo) riskInfo.style.display = 'none';
        // Actualizar estado
        if (statusBadge) statusBadge.textContent = 'INACTIVO';
        if (signalCard) signalCard.classList.remove('active');
        return;
    }

    // Actualizar datos básicos
    const priceEl = document.getElementById(`${type}-price`);
    const timeEl = document.getElementById(`${type}-time`);
    const rsiEl = document.getElementById(`${type}-rsi`);
    const macdEl = document.getElementById(`${type}-macd`);

    if (priceEl) priceEl.textContent = signalData.price ? formatNumber(signalData.price, 2) : '--';
    if (timeEl) timeEl.textContent = signalData.time_iso ? formatTime(signalData.time_iso) : '--:--';
    if (rsiEl) rsiEl.textContent = signalData.rsi ? formatNumber(signalData.rsi, 2) : '--';
    if (macdEl) macdEl.textContent = signalData.macd ? formatNumber(signalData.macd, 4) : '--';

    // Mostrar sección de riesgo si hay información de stop loss
    if (riskInfo && stopLossInfo && stopLossInfo.active &&
        ((type === 'buy' && stopLossInfo.is_buy) || (type === 'sell' && !stopLossInfo.is_buy))) {

        const entryPrice = parseFloat(stopLossInfo.entry_price);
        const stopLoss = parseFloat(stopLossInfo.stop_loss);
        const takeProfit = parseFloat(stopLossInfo.take_profit);

        // Calcular distancia al stop loss
        const distanceToSL = Math.abs(currentPrice - stopLoss);
        const distancePercent = (distanceToSL / entryPrice * 100).toFixed(2);

        // Determinar nivel de alerta
        let alertClass = 'text-success';
        let progressClass = 'bg-success';

        if (distancePercent < 0.3) {
            alertClass = 'text-danger';
            progressClass = 'bg-danger';
        } else if (distancePercent < 0.5) {
            alertClass = 'text-warning';
            progressClass = 'bg-warning';
        }

        // Actualizar elementos de riesgo
        const slEl = document.getElementById(`${type}-sl`);
        const tpEl = document.getElementById(`${type}-tp`);
        const progressEl = document.getElementById(`${type}-progress`);
        const distanceEl = document.getElementById(`${type}-distance`);

        if (slEl) slEl.textContent = stopLoss.toFixed(4);
        if (tpEl) tpEl.textContent = takeProfit.toFixed(4);

        if (progressEl) {
            progressEl.className = `progress-bar ${progressClass}`;
            progressEl.style.width = `${Math.min(100, distancePercent * 2)}%`;
        }

        if (distanceEl) {
            distanceEl.className = alertClass;
            distanceEl.textContent = type === 'buy'
                ? `Precio actual: ${currentPrice.toFixed(4)} (${distancePercent}% al SL)`
                : `Precio actual: ${currentPrice.toFixed(4)} (${distancePercent}% al SL)`;
        }

        // Mostrar la sección de riesgo
        riskInfo.style.display = 'block';
    } else if (riskInfo) {
        // Ocultar la sección de riesgo si no hay información relevante
        riskInfo.style.display = 'none';
    }

    // Actualizar estado
    if (statusBadge) {
        statusBadge.textContent = 'ACTIVO';
        statusBadge.className = 'text-success fw-bold';
    }

    // Limpiar íconos huérfanos y asegurar que todos los íconos de condición tengan la clase correcta
    document.querySelectorAll('.condition-item i').forEach(icon => {
        if (!icon.classList.contains('condition-icon')) {
            icon.remove();
        }
    });

    if (signalCard) signalCard.classList.add('active');
}

// Función para actualizar recomendaciones
function updateRecommendations(data) {
    const recommendationsEl = document.getElementById('recommendations');
    if (!recommendationsEl) return;

    let html = '';
    const indicators = data.indicators || {};
    const buySignal = data.buy_signal || {};
    const sellSignal = data.sell_signal || {};
    const lastPrice = parseFloat(data.last_price) || 0;

    // Mostrar indicadores técnicos
    if (indicators) {
        html += `
                <div class="card mb-3">
                    <div class="card-header bg-dark text-white">
                        <i class="fas fa-chart-line me-2"></i>Indicadores Técnicos
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-2"><strong>RSI:</strong> ${formatNumber(indicators.rsi || 0, 2)}</div>
                                <div class="mb-2"><strong>ADX:</strong> ${formatNumber(indicators.adx || 0, 2)} (${indicators.trend_strength || 'N/A'})</div>
                                <div class="mb-2"><strong>MACD:</strong> ${formatNumber(indicators.macd || 0, 4)}</div>
                                <div class="mb-2"><strong>Señal MACD:</strong> ${formatNumber(indicators.macd_signal || 0, 4)}</div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-2"><strong>SMA 20:</strong> ${formatNumber(indicators.sma_20 || 0, 2)}</div>
                                <div class="mb-2"><strong>SMA 50:</strong> ${formatNumber(indicators.sma_50 || 0, 2)}</div>
                                <div class="mb-2"><strong>ATR:</strong> ${formatNumber(indicators.atr || 0, 2)}</div>
                                ${indicators.ai_prediction ?
                `<div class="mt-3 p-2 rounded ${indicators.ai_prediction.direction === 'ALCISTA' ? 'bg-success' : 'bg-danger'} bg-opacity-25">
                                        <strong>Predicción IA:</strong> ${indicators.ai_prediction.direction} 
                                        <small class="d-block">Cambio: ${formatNumber(indicators.ai_prediction.change * 100, 4)}%</small>
                                        <small class="d-block">Confianza: ${formatNumber(indicators.ai_prediction.confidence * 100, 2)}%</small>
                                    </div>` : ''
            }
                            </div>
                        </div>
                    </div>
                </div>`;
    }

    // Estructura base para las recomendaciones
    const recommendations = [];

    // Análisis de la señal de compra
    if (buySignal.active) {
        const rsi = parseFloat(buySignal.rsi) || 0;
        const macd = parseFloat(buySignal.macd) || 0;
        const macdSignal = parseFloat(data.macd_signal) || 0;
        const price = parseFloat(buySignal.price) || lastPrice;
        const time = buySignal.time_iso ? formatTime(buySignal.time_iso) : 'Reciente';

        let analysis = [];
        if (rsi < 30) analysis.push(`RSI muy bajo (${formatNumber(rsi, 2)}) - Mercado sobrevendido`);
        if (macd > macdSignal) analysis.push(`Cruce alcista del MACD (${formatNumber(macd, 4)} > ${formatNumber(macdSignal, 4)})`);
        if (data.sma_20 > data.sma_50) analysis.push(`Media móvil corta (${formatNumber(data.sma_20, 2)}) por encima de la larga (${formatNumber(data.sma_50, 2)})`);

        recommendations.push({
            type: 'buy',
            title: 'Señal de COMPRA detectada',
            price: price,
            time: time,
            analysis: analysis.length > 0 ? analysis : ['Patrón de compra detectado'],
            strength: analysis.length * 25 // Puntuación de 0-100
        });
    }

    // Análisis de la señal de venta
    if (sellSignal.active) {
        const rsi = parseFloat(sellSignal.rsi) || 0;
        const macd = parseFloat(sellSignal.macd) || 0;
        const macdSignal = parseFloat(data.macd_signal) || 0;
        const price = parseFloat(sellSignal.price) || lastPrice;
        const time = sellSignal.time_iso ? formatTime(sellSignal.time_iso) : 'Reciente';

        let analysis = [];
        if (rsi > 70) analysis.push(`RSI muy alto (${formatNumber(rsi, 2)}) - Mercado sobrecomprado`);
        if (macd < macdSignal) analysis.push(`Cruce bajista del MACD (${formatNumber(macd, 4)} < ${formatNumber(macdSignal, 4)})`);
        if (data.sma_20 < data.sma_50) analysis.push(`Media móvil corta (${formatNumber(data.sma_20, 2)}) por debajo de la larga (${formatNumber(data.sma_50, 2)})`);

        recommendations.push({
            type: 'sell',
            title: 'Señal de VENTA detectada',
            price: price,
            time: time,
            analysis: analysis.length > 0 ? analysis : ['Patrón de venta detectado'],
            strength: analysis.length * 25 // Puntuación de 0-100
        });
    }

    // Generar HTML de recomendaciones
    if (recommendations.length > 0) {
        recommendations.forEach(rec => {
            const alertClass = rec.type === 'buy' ? 'success' : 'danger';
            const icon = rec.type === 'buy' ? 'arrow-up' : 'arrow-down';

            html += `
                    <div class="alert alert-${alertClass} mb-3">
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-${icon} fa-2x me-3"></i>
                            <div>
                                <h5 class="mb-0">${rec.title}</h5>
                                <div class="small">${rec.time} - Fuerza: ${rec.strength}%</div>
                            </div>
                        </div>
                        <div class="mt-2">
                            <div class="fw-bold mb-1">Precio: ${formatNumber(rec.price, 2)} USDT</div>
                            <ul class="mb-0 ps-3">
                                ${rec.analysis.map(item => `<li>${item}</li>`).join('')}
                            </ul>
                        </div>
                    </div>`;
        });

        // Añadir advertencia de riesgo
        html += `
                <div class="alert alert-warning mt-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Advertencia de riesgo:</strong> Las señales de trading no son una garantía de rendimiento. 
                    Siempre realice su propio análisis y gestione el riesgo adecuadamente.
                </div>`;

    } else {
        // No hay señales activas
        html = `
                <div class="alert alert-info">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-info-circle fa-2x me-3"></i>
                        <div>
                            <h5 class="mb-1">Sin señales activas</h5>
                            <p class="mb-0">El bot está monitoreando el mercado en busca de oportunidades de trading.</p>
                        </div>
                    </div>
                </div>`;

    }

    // Actualizar el DOM
    if (recommendationsEl) {
        recommendationsEl.innerHTML = html;
    }
}

// Función para actualizar configuración
function updateSettings() {
    const symbol = document.getElementById('symbol').value;
    const timeframe = document.getElementById('timeframe').value;

    // Aquí podrías enviar esta configuración al servidor
    // Por ahora, solo actualizamos los datos
    updateData();
}

// Cargar datos iniciales
document.addEventListener('DOMContentLoaded', function () {
    // Inicializar valores por defecto inmediatamente
    initializeDefaultValues();

    // Luego cargar datos reales
    updateData();

    // Actualizar datos cada 60 segundos
    setInterval(updateData, 60000);
});

// Update the 'Análisis Avanzado' section to display data from app.py
const updateAdvancedAnalysis = (data) => {
    const indicators = data.indicators || {};

    // Update RSI card
    const rsiValue = indicators.rsi ? indicators.rsi.toFixed(2) : 'N/A';
    document.getElementById('rsi-value').textContent = rsiValue;
    document.getElementById('rsi-interpretation').textContent = rsiValue <= 30
        ? 'Sobrevendido - Posible oportunidad de compra'
        : rsiValue >= 70
            ? 'Sobrecomprado - Posible oportunidad de venta'
            : 'Neutral - Mercado en equilibrio';

    // Update RSI progress bar
    const rsiBar = document.getElementById('rsi-bar');
    if (indicators.rsi !== undefined && indicators.rsi !== null) {
        const rsiPercent = Math.min(100, Math.max(0, indicators.rsi));
        rsiBar.style.width = `${rsiPercent}%`;

        // Color coding based on RSI value
        if (indicators.rsi <= 30) {
            rsiBar.className = 'progress-bar bg-danger'; // Red for oversold
        } else if (indicators.rsi >= 70) {
            rsiBar.className = 'progress-bar bg-success'; // Green for overbought
        } else {
            rsiBar.className = 'progress-bar bg-warning'; // Yellow for neutral
        }
    } else {
        rsiBar.style.width = '0%';
        rsiBar.className = 'progress-bar';
    }

    // Update MACD card
    const macdValue = indicators.macd ? indicators.macd.toFixed(4) : 'N/A';
    const macdSignalValue = indicators.macd_signal ? indicators.macd_signal.toFixed(4) : 'N/A';
    document.getElementById('macd-value').textContent = macdValue;
    document.getElementById('macd-signal-value').textContent = macdSignalValue;
    document.getElementById('macd-interpretation').textContent = macdValue > macdSignalValue
        ? 'Señal alcista: MACD por encima de la línea de señal'
        : macdValue < macdSignalValue
            ? 'Señal bajista: MACD por debajo de la línea de señal'
            : 'Cruce potencial: MACD cerca de la línea de señal';

    // Update ADX card
    const adxValue = indicators.adx ? indicators.adx.toFixed(2) : 'N/A';
    document.getElementById('adx-value').textContent = adxValue;
    document.getElementById('adx-interpretation').textContent = adxValue >= 50
        ? 'Tendencia muy fuerte - Buenas condiciones para trading'
        : adxValue >= 25
            ? 'Tendencia moderada - Considerar operaciones con precaución'
            : 'Tendencia débil - Mercado lateral, trading riesgoso';

    // Update ATR card
    const atrValue = indicators.atr ? indicators.atr.toFixed(4) : 'N/A';
    document.getElementById('atr-value').textContent = atrValue;
    document.getElementById('atr-interpretation').textContent = atrValue < 0.5
        ? 'Volatilidad baja - Condiciones estables para trading'
        : atrValue < 1
            ? 'Volatilidad moderada - Ajustar stop loss según corresponda'
            : 'Volatilidad alta - Precaución, mayor riesgo';

    // Update AI Prediction card
    const aiPrediction = indicators.ai_prediction || {};
    const predictionValue = aiPrediction.prediction || 'N/A';
    const confidenceValue = aiPrediction.confidence ? Math.min(Math.max(aiPrediction.confidence * 100, 0), 100) : 0;
    const confidenceText = confidenceValue.toFixed(1) + '%';

    // Determine action based on prediction and confidence
    let actionText = 'Esperar';
    let actionReason = 'No hay suficiente información para tomar una decisión';
    let actionClass = 'alert-secondary';

    if (predictionValue.toLowerCase().includes('alcista')) {
        if (confidenceValue >= 80) {
            actionText = '🔥 COMPRAR FUERTE';
            actionReason = 'Señal de compra con alta confianza';
            actionClass = 'alert-success';
        } else if (confidenceValue >= 60) {
            actionText = '✅ COMPRAR';
            actionReason = 'Señal de compra con confianza moderada';
            actionClass = 'alert-success';
        } else if (confidenceValue >= 40) {
            actionText = '⚠️ COMPRAR CON CUIDADO';
            actionReason = 'Señal de compra con baja confianza';
            actionClass = 'alert-warning';
        } else {
            actionText = '❌ NO COMPRAR';
            actionReason = 'Señal de compra con muy baja confianza';
            actionClass = 'alert-danger';
        }
    } else if (predictionValue.toLowerCase().includes('bajista')) {
        if (confidenceValue >= 80) {
            actionText = '🔥 VENDER FUERTE';
            actionReason = 'Señal de venta con alta confianza';
            actionClass = 'alert-danger';
        } else if (confidenceValue >= 60) {
            actionText = '✅ VENDER';
            actionReason = 'Señal de venta con confianza moderada';
            actionClass = 'alert-danger';
        } else if (confidenceValue >= 40) {
            actionText = '⚠️ VENDER CON CUIDADO';
            actionReason = 'Señal de venta con baja confianza';
            actionClass = 'alert-warning';
        } else {
            actionText = '❌ NO VENDER';
            actionReason = 'Señal de venta con muy baja confianza';
            actionClass = 'alert-secondary';
        }
    }

    // Update UI elements
    const predictionElement = document.getElementById('ai-prediction-value');
    predictionElement.textContent = predictionValue;
    predictionElement.className = predictionValue.toLowerCase().includes('alcista') ? 'text-success' : 'text-danger';
    document.getElementById('ai-prediction-action').textContent = '';
    document.getElementById('ai-confidence-badge').textContent = `Confianza: ${confidenceText}`;
    document.getElementById('ai-confidence-badge').className = confidenceValue >= 80
        ? 'badge bg-success'
        : confidenceValue >= 60
            ? 'badge bg-info'
            : confidenceValue >= 40
                ? 'badge bg-warning'
                : 'badge bg-danger';

    // Update action recommendation
    const aiRecommendation = document.getElementById('ai-recommendation');
    const aiActionText = document.getElementById('ai-action-text');
    const aiActionReason = document.getElementById('ai-action-reason');

    if (aiRecommendation && aiActionText && aiActionReason) {
        aiActionText.textContent = actionText;
        aiActionReason.textContent = actionReason;
        aiRecommendation.className = `alert text-center mb-0 ${actionClass}`;
        aiRecommendation.style.display = 'block';
    }

    // Update AI confidence progress bar
    const aiConfidenceBar = document.getElementById('ai-confidence-bar');
    if (aiConfidenceBar) {
        aiConfidenceBar.style.width = `${confidenceValue}%`;
        aiConfidenceBar.setAttribute('aria-valuenow', confidenceValue);
        aiConfidenceBar.setAttribute('title', `Confianza: ${confidenceText}`);

        // Color coding based on confidence level
        if (confidenceValue >= 80) {
            aiConfidenceBar.className = 'progress-bar bg-success';
        } else if (confidenceValue >= 60) {
            aiConfidenceBar.className = 'progress-bar bg-info';
        } else if (confidenceValue >= 40) {
            aiConfidenceBar.className = 'progress-bar bg-warning';
        } else {
            aiConfidenceBar.className = 'progress-bar bg-danger';
        }
    }

    // Update Market Status card
    const trendStatus = indicators.trend_strength || 'Indeterminado';
    document.getElementById('trend-status-value').textContent = trendStatus;
    const marketTrendBadge = document.getElementById('market-trend-badge');
    marketTrendBadge.textContent = trendStatus;
    marketTrendBadge.className = trendStatus.toLowerCase().includes('alcista')
        ? 'badge bg-success'
        : trendStatus.toLowerCase().includes('bajista')
            ? 'badge bg-danger'
            : 'badge bg-secondary';
};

// Call the function with the data received from the backend
fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        updateAdvancedAnalysis(data);

        // Call updateAIRecommendations with initial data
        if (data.recommendations) {
            updateAIRecommendations(data.recommendations);
        }
    })
    .catch(error => console.error('Error fetching data:', error));

// Función para actualizar recomendaciones de IA
function updateAIRecommendations(recommendations) {
    const recommendationsEl = document.getElementById('recommendations');
    if (!recommendationsEl) return;

    if (recommendations.length === 0) {
        recommendationsEl.innerHTML = '<p>No hay recomendaciones disponibles en este momento.</p>';
        return;
    }

    let html = '';
    recommendations.forEach(rec => {
        const alertClass = rec.type === 'buy' ? 'success' : 'danger';
        html += `
                        <div class="alert alert-${alertClass} mb-3">
                            <strong>${rec.title}</strong><br>
                            Precio: ${rec.price}<br>
                            Hora: ${rec.time}<br>
                            <ul>
                                ${rec.analysis.map(a => `<li>${a}</li>`).join('')}
                            </ul>
                        </div>`;
    });

    recommendationsEl.innerHTML = html;
}
