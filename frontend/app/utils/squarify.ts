export interface WeightedItem<T> {
  item: T
  weight: number
}

export interface PlacedItem<T> {
  item: T
  left: number
  top: number
  width: number
  height: number
}

interface Rect {
  left: number
  top: number
  width: number
  height: number
}

interface Sized<T> {
  item: T
  area: number
}

function worstRatio<T>(row: Sized<T>[], shortSide: number): number {
  const sum = row.reduce((total, cell) => total + cell.area, 0)
  const ratios = row.map((cell) => {
    const squaredSide = shortSide * shortSide
    return Math.max((squaredSide * cell.area) / (sum * sum), (sum * sum) / (squaredSide * cell.area))
  })
  return Math.max(...ratios)
}

/** Prend la plus longue rangée qui garde des tuiles proches du carré. */
function takeRow<T>(cells: Sized<T>[], shortSide: number): Sized<T>[] {
  const row: Sized<T>[] = []
  for (const cell of cells) {
    if (row.length && worstRatio([...row, cell], shortSide) > worstRatio(row, shortSide)) break
    row.push(cell)
  }
  return row
}

/** Pose une rangée sur le petit côté et renvoie la place restante. */
function placeRow<T>(row: Sized<T>[], rect: Rect, placed: PlacedItem<T>[]): Rect {
  const isWide = rect.width >= rect.height
  const rowArea = row.reduce((total, cell) => total + cell.area, 0)
  const thickness = rowArea / (isWide ? rect.height : rect.width)
  let offset = 0
  for (const cell of row) {
    const length = cell.area / thickness
    placed.push({
      item: cell.item,
      left: rect.left + (isWide ? 0 : offset),
      top: rect.top + (isWide ? offset : 0),
      width: isWide ? thickness : length,
      height: isWide ? length : thickness
    })
    offset += length
  }
  return isWide
    ? { ...rect, left: rect.left + thickness, width: rect.width - thickness }
    : { ...rect, top: rect.top + thickness, height: rect.height - thickness }
}

/** Treemap « squarified » : les poids décroissants donnent les surfaces, en % du conteneur. */
export function squarify<T>(items: WeightedItem<T>[], aspectRatio: number): PlacedItem<T>[] {
  const FULL = 100
  const totalWeight = items.reduce((total, entry) => total + entry.weight, 0)
  if (totalWeight <= 0) return []

  let rect: Rect = { left: 0, top: 0, width: FULL * aspectRatio, height: FULL }
  const scale = (rect.width * rect.height) / totalWeight
  let cells = items.map(({ item, weight }) => ({ item, area: weight * scale }))
  const placed: PlacedItem<T>[] = []

  while (cells.length) {
    const row = takeRow(cells, Math.min(rect.width, rect.height))
    rect = placeRow(row, rect, placed)
    cells = cells.slice(row.length)
  }

  return placed.map((cell) => ({
    ...cell,
    left: cell.left / aspectRatio,
    width: cell.width / aspectRatio
  }))
}
