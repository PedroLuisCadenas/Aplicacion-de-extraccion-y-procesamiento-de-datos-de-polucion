// Configuración global de la aplicación Angular

import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';

import { routes } from './app.routes';
import { apiKeyInterceptor } from './core/api-key.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(), // captura errores globales
    provideZoneChangeDetection({ eventCoalescing: true }), 
    provideRouter(routes), // enrutador con las rutas de app.routes.ts
    provideHttpClient(withInterceptors([apiKeyInterceptor])), // HTTPClient con interceptor
    provideCharts(withDefaultRegisterables()) // registra los tipos/escala de Chart.js
  ]
};
