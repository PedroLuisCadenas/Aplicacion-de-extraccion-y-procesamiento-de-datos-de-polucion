import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { Api, DeviceElement, ReadingsHistoryPoint, ReadingsHistoryParams } from '../../core/api';
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

function toDatetimeLocalInput (date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
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
  protected readonly mode = signal<'hours' | 'range'>('hours');
  protected readonly rangeStart = signal<string>('');
  protected readonly rangeEnd = signal<string>('');
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
    else if (this.selectedHourPresets() !== 'custom') {
      this.loadReadings();
    }
  }

  selectHoursPreset(preset: number | 'custom'): void {
    this.selectedHourPresets.set(preset);
    if (preset !== 'custom') {
      this.hours.set(preset);
      if (this.selectedElementId()) {
        this.loadReadings();
      }
    }
  }

    onCustomModeChange(newMode: 'hours' | 'range'): void {
    this.mode.set(newMode);
    this.readings.set([]);
  }


    loadReadings(): void {
    const elementId = this.selectedElementId();

    if (!elementId) {
      this.error.set('Selecciona un sensor antes de consultar.');
      return;
    }

    let params: ReadingsHistoryParams;
    if (this.selectedHourPresets() !== 'custom' || this.mode() === 'hours') {
      params = { hours: this.hours() };
    } else {
      if (!this.rangeStart()) {
        this.error.set('Indica al menos la fecha/hora de inicio del rango.');
        return;
      }
      if (!this.rangeEnd()) {
        this.rangeEnd.set(toDatetimeLocalInput(new Date()));
      }
      params = {
        start: new Date(this.rangeStart()).toISOString(),
        end: new Date(this.rangeEnd()).toISOString(),
      };
    }

    this.loading.set(true);
    this.error.set(null);

    this.api.getReadingsHistory(params, elementId).subscribe({
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
