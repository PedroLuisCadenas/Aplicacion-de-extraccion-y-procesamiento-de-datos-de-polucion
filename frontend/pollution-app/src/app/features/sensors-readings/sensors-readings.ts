import { Component, inject, signal, OnInit } from '@angular/core';
import { Api, DeviceElement, ElementRead } from '../../core/api';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-sensors-readings',
  imports: [FormsModule, DatePipe],
  templateUrl: './sensors-readings.html',
  styleUrl: './sensors-readings.css',
})
export class SensorsReadings implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly selectedElementId = signal<string | ''>('');
  protected readonly hours = signal<number>(24);
  protected readonly readings = signal<ElementRead[]>([]);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

  loadReadings(): void {
    const elementId = this.selectedElementId();

    if (!elementId) {
      this.error.set('Selecciona un sensor antes de consultar.');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    this.api.getElementReadings(elementId, this.hours()).subscribe({
      next: (readings) => {
        this.readings.set(readings);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se han podido cargar las lecturas del sensor.');
        this.loading.set(false);
      },
    });
  }

  ngOnInit(): void {
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
  }
    
  
}
