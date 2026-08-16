import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ChartConfiguration, ChartData } from 'chart.js';
import 'chartjs-adapter-date-fns';
import { Api, DeviceElement, ReadingsHistoryParams, ReadingsHistoryPoint } from '../../core/api';
import { FormsModule } from '@angular/forms';
import { BaseChartDirective } from 'ng2-charts';
import { DatePipe } from '@angular/common';

type RangeMode = 'hours' | 'range';

interface SensorStat {
  id: string;
  label: string;
  avg: number;
  min: number;
  max: number;
}

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

function toDatetimeLocalInput(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toCsvValue(value: string | number): string {
  return typeof value === 'number' ? value.toString().replace('.', ',') : value;
}

@Component({
  selector: 'app-charts',
  imports: [FormsModule, BaseChartDirective, DatePipe],
  templateUrl: './charts.html',
  styleUrl: './charts.css',
})
export class Charts implements OnInit {
  private readonly api = inject(Api);

  protected readonly deviceElements = signal<DeviceElement[]>([]);
  protected readonly selectedIds = signal<Set<string>>(new Set());
  protected readonly mode = signal<RangeMode>('hours');
  protected readonly hours = signal<number>(24);
  protected readonly rangeStart = signal<string>('');
  protected readonly rangeEnd = signal<string>('');
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly isPickerOpen = signal(false);
  protected readonly pickerSearch = signal('');
  protected readonly draftSelectedIds = signal<Set<string>>(new Set());
  protected readonly historyRows = signal<ReadingsHistoryPoint[]>([]);
  protected readonly currentPage = signal(1);
  private readonly PAGE_SIZE = 5;

  protected readonly lineChartOptions: ChartConfiguration<'line'>['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'time',
        time: { tooltipFormat: 'dd/MM/yyyy HH:mm' },
        ticks: { autoSkip: true, maxRotation: 0 },
      },
    },
  };

  ngOnInit(): void {
    this.api.getDeviceElements().subscribe({
      next: (elements) => this.deviceElements.set(elements),
      error: () => this.error.set('No se han podido cargar los sensores del dispositivo.'),
    });
  }

  protected readonly intervalStats = computed(() => {
  return this.selectedSensorChips()
    .map((element): SensorStat | null => {
      const values = this.historyRows()
        .filter((row) => row[element.id] != null)
        .map((row) => row[element.id] as number);

      if (values.length === 0) {
        return null;
      }

      const sum = values.reduce((total, value) => total + value, 0);
      return {
        id: element.id,
        label: element.unit ? `${element.name} (${element.unit})` : element.name,
        avg: round2(sum / values.length),
        min: round2(Math.min(...values)),
        max: round2(Math.max(...values)),
      };
    })
    .filter((stat): stat is SensorStat => stat !== null);
  });

  protected readonly lineChartData = computed(() => {
    const datasets = this.deviceElements()
          .filter((element) => this.selectedIds().has(element.id))
          .map((element) => ({
            label: element.unit ? `${element.name} (${element.unit})` : element.name,
            data: this.historyRows()
              .filter((row) => row[element.id] != null)
              .map((row) => ({
                x: new Date(row.time).getTime(),
                y: row[element.id] as number,
              })),
          }));
    return { datasets };      
  });        

  protected readonly selectedSensorChips = computed(() =>
    this.deviceElements().filter((element) => this.selectedIds().has(element.id)),
  );

  protected readonly filteredElements = computed(() => {
    const search = this.pickerSearch().toLowerCase();
    return this.deviceElements().filter((element) => element.name.toLowerCase().includes(search));
  });

  protected readonly paginatedHistoryRows = computed(() => {
    const startIndex = (this.currentPage() - 1) * this.PAGE_SIZE;
    return this.historyRows().slice(startIndex, startIndex + this.PAGE_SIZE);
  });

  protected readonly totalPages = computed(() => {
    return Math.ceil(this.historyRows().length / this.PAGE_SIZE);
  });

  protected readonly pageRangeStart = computed(() => {
    if (this.historyRows().length === 0) {
      return 0;
    }
    return (this.currentPage() - 1) * this.PAGE_SIZE + 1;
  });

  protected readonly pageRangeEnd = computed(() => {
    return Math.min(this.currentPage() * this.PAGE_SIZE, this.historyRows().length);
  });

  toggleSensor(id: string): void {
    const selectedIds = new Set(this.selectedIds());
    if (selectedIds.has(id)) {
      selectedIds.delete(id);
    } else {
      selectedIds.add(id);
    }
    this.selectedIds.set(selectedIds);
  }

  clearSelection(): void {
    this.selectedIds.set(new Set());
    this.historyRows.set([]);
  }

  openPicker(): void {
    this.draftSelectedIds.set(new Set(this.selectedIds()));
    this.isPickerOpen.set(true);
  }

  closePicker(): void {
    this.isPickerOpen.set(false);
  }

  applyPicker(): void {
    this.selectedIds.set(new Set(this.draftSelectedIds()));
    this.isPickerOpen.set(false);
  }

  toggleDraftSensor(id: string): void {
    const draftSelectedIds = new Set(this.draftSelectedIds());
    if (draftSelectedIds.has(id)) {
      draftSelectedIds.delete(id);
    } else {
      draftSelectedIds.add(id);
    }
    this.draftSelectedIds.set(draftSelectedIds);
  }

  onModeChange(newMode: RangeMode): void {
    this.mode.set(newMode);
    this.historyRows.set([]);
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
    }
  }

  downloadCSV(): void {
    const sensorLabels = this.selectedSensorChips().map((element) =>
      element.unit ? `${element.name} (${element.unit})` : element.name,
    );
    const header = ['Fecha', ...sensorLabels];
    const dataRows = this.historyRows().map((row) => {
      const values = this.selectedSensorChips().map((element) => toCsvValue(row[element.id] ?? ''));
      return [row.time, ...values];
    });
    const allRows = [header, ...dataRows];
    const csvContent = allRows.map((row) => row.join(';')).join('\n');
    const csvWithBom = '\uFEFF' + csvContent; // Add BOM for Excel compatibility
    const blob = new Blob([csvWithBom], { type: 'text/csv;charset=utf-8;' }); 
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `comparador-sensores-${new Date().toISOString().slice(0, 19)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  generateChart(): void {
    if (this.selectedIds().size === 0) {
      this.error.set('Selecciona al menos un sensor antes de generar el gráfico.');
      return;
    }

    let params: ReadingsHistoryParams;
    if (this.mode() === 'hours') {
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

    this.api.getReadingsHistory(params).subscribe({
      next: (rows) => {
        this.historyRows.set(rows);
        this.currentPage.set(1);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se han podido cargar los datos del histórico.');
        this.loading.set(false);
      },
    });
  }

}
