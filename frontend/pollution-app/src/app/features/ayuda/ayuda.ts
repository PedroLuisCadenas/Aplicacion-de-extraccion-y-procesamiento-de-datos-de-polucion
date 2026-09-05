import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { Api, DeviceElement } from '../../core/api';
import { SENSOR_DESCRIPTIONS } from '../../core/sensor-catalog';

@Component({
  selector: 'app-ayuda',
  imports: [],
  templateUrl: './ayuda.html',
  styleUrl: './ayuda.css',
})
export class Ayuda implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly error = signal<string | null>(null);
  protected readonly currentPage = signal(1);
  private readonly PAGE_SIZE = 10;

  protected readonly sensorCatalog = computed(() => {
    const elements = this.deviceElements();
    return elements.map((element) => ({
      id: element.id,
      name: element.name,
      unit: element.unit,
      description: SENSOR_DESCRIPTIONS[element.id] ?? 'Descripción no disponible',
    }));
  });

  protected readonly paginatedSensorCatalog = computed(() => {
    const startIndex = (this.currentPage() - 1) * this.PAGE_SIZE;
    return this.sensorCatalog().slice(startIndex, startIndex + this.PAGE_SIZE);
  });

  protected readonly totalPages = computed(() => {
    return Math.ceil(this.sensorCatalog().length / this.PAGE_SIZE);
  });

  protected readonly pageRangeStart = computed(() => {
    if (this.sensorCatalog().length === 0) {
      return 0;
    }
    return (this.currentPage() - 1) * this.PAGE_SIZE + 1;
  });

  protected readonly pageRangeEnd = computed(() => {
    return Math.min(this.currentPage() * this.PAGE_SIZE, this.sensorCatalog().length);
  });

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  ngOnInit(): void {
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
  }
}
