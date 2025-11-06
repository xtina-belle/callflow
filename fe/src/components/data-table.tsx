"use client";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {ChevronLeft, ChevronRight} from "lucide-react";
import React from "react";

import {Button} from "@/components/ui/button";
import {Skeleton} from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface TableSkeletonProps {
  rows: number;
  columns: number;
}

function TableSkeleton({rows, columns}: TableSkeletonProps) {
  return (
    <div className="w-full">
      <div className="max-h-[600px] overflow-auto relative">
        <table className="w-full caption-bottom text-sm">
          <thead className="bg-background border-b">
          <tr className="bg-background">
            {Array.from({length: columns}).map((_, index) => (
              <th
                key={index}
                className="h-12 px-4 text-left align-middle bg-background"
              >
                <Skeleton className="h-4 w-full max-w-[120px]"/>
              </th>
            ))}
          </tr>
          </thead>
          <tbody>
          {Array.from({length: rows}).map((_, rowIndex) => (
            <tr key={rowIndex} className="border-b">
              {Array.from({length: columns}).map((_, colIndex) => (
                <td key={colIndex} className="p-4 align-middle">
                  <Skeleton className="h-4 w-full"/>
                </td>
              ))}
            </tr>
          ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  onRowClick: (data: TData) => void
  isLoading: boolean
}

export function DataTable<TData, TValue>({
                                           columns,
                                           data,
                                           onRowClick,
                                           isLoading,
                                         }: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  if (isLoading) {
    return <TableSkeleton rows={7} columns={5}/>
  }

  return (
    <div>
      <div className="rounded-md">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className="font-medium text-muted-foreground">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  onClick={() => onRowClick(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {table.getPageCount() > 1 &&
          <div className="flex items-center justify-end py-4">
              <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => table.previousPage()}
                  disabled={!table.getCanPreviousPage()}
              >
                  <ChevronLeft className="mr-2 h-4 w-4"/>
                  Previous
              </Button>
              <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => table.nextPage()}
                  disabled={!table.getCanNextPage()}
              >
                  Next
                  <ChevronRight className="ml-2 h-4 w-4"/>
              </Button>
          </div>
      }

    </div>
  )
}
