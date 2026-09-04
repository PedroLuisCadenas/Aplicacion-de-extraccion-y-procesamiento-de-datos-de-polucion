import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { Api, DeviceElement, ReadingsHistoryPoint } from '../../core/api';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';

const HOUR_PRESETS: { value: number; label: string }[] = [
  { value: 6, label: '6 h' },
  { value: 12, label: '12 h' },
  { value: 24, label: '24 h' },
  { value: 48, label: '48 h' },
  { value: 168, label: '7 días' },
];

function toCsvValue(value: string | number): string {
  return typeof value === 'number' ? value.toString().replace('.', ',') : value;
}

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
  protected readonly hours = signal<number>(6);
  protected readonly selectedHourPresets = signal<number | 'custom'>(6);
  protected readonly hourPresets = HOUR_PRESETS;
  protected readonly readings = signal<ReadingsHistoryPoint[]>([]);
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);

 protected readonly selectedElement = computed(
  () => this.deviceElements().find((element) => element.id === this.selectedElementId()) ?? null,
);

  onSensorChange(id: string): void {
    this.selectedElementId.set(id);
    if (!id) {
      this.readings.set([]);
      this.error.set(null);
    }
  }

  selectHoursPreset(preset: number | 'custom'): void {
    this.selectedHourPresets.set(preset);
    if (preset !== 'custom') {
      this.hours.set(preset);
    }
  }

  loadReadings(): void {
    const elementId = this.selectedElementId();

    if (!elementId) {
      this.error.set('Selecciona un sensor antes de consultar.');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    this.api.getReadingsHistory({ hours: this.hours() }, elementId).subscribe({
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

  downloadCSV(): void {
    const element = this.selectedElement();
    if (!element) {
      return;
    }

    const sensorLabel = element.unit ? `${element.name} (${element.unit})` : element.name;
    const header = ['Fecha', sensorLabel];
    const dataRows = this.readings().map((row) => [row.time, toCsvValue(row[element.id] ?? '')]);
    const allRows = [header, ...dataRows];
    const csvContent = allRows.map((row) => row.join(';')).join('\n');
    const csvWithBom = '\uFEFF' + csvContent;
    const blob = new Blob([csvWithBom], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `lecturas-${element.id}-${new Date().toISOString().slice(0, 19)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }
}
