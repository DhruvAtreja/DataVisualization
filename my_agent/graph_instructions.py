
barGraphIntstruction = '''
interface HorizontalBarGraphProps {
  data: {
    labels: string[]
    values: number[]
  }
}
// Example usage:
export exampleData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  values: [21.5, 25.0, 47.5, 64.8, 105.5, 133.2],
}
'''

horizontalBarGraphIntstruction = '''
export interface HorizontalBarGraphProps {
  data: {
    labels: string[]
    values: number[]
  }
}
// Example usage:
export exampleData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  values: [21.5, 25.0, 47.5, 64.8, 105.5, 133.2],
}
'''

lineGraphIntstruction = '''
export interface LineGraphProps {
  data: {
    labels: string[]
    values: number[]
  }
}

// Example usage:
export exampleData = {
  labels: ['1', '2', '3', '5', '8', '10'],
  values: [2, 5.5, 2, 8.5, 1.5, 5],
}
'''

pieChartIntstruction = '''
export interface PieChartProps {
  data: {
    labels: string[]
    values: number[]
  }
}

// Example usage:
export exampleData = {
  labels: ['series A', 'series B', 'series C'],
  values: [10, 15, 20],
}

'''

scatterPlotIntstruction = '''
interface ScatterPlotData {
  x: number
  y: number
  label: string
}

export interface ScatterPlotProps {
  data: ScatterPlotData[][]
}

// Example usage:
export exampleData: ScatterPlotData[][] = [
  [
    { x: 100, y: 200, label: 'Point 1' },
    { x: 120, y: 100, label: 'Point 2' },
    { x: 170, y: 300, label: 'Point 3' },
    { x: 140, y: 250, label: 'Point 4' },
    { x: 150, y: 400, label: 'Point 5' },
    { x: 110, y: 280, label: 'Point 6' },
  ],
]
'''




graph_instructions = {
    "bar": barGraphIntstruction,
    "horizontal_bar": horizontalBarGraphIntstruction,
    "line": lineGraphIntstruction,
    "pie": pieChartIntstruction,
    "scatter": scatterPlotIntstruction
}