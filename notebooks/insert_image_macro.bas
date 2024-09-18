
Sub InsertImageFromURL()
    Dim imgPath As String
    imgPath = "https://img.rewe-static.de/0108820/23174444_digital-image.png?resize=152px:152px&output-quality=80&output-format=jpeg&im=BackgroundColor,color=fffff"
    With ActiveSheet.Pictures.Insert(imgPath)
        .ShapeRange.LockAspectRatio = msoFalse
        .ShapeRange.Width = Range("A1").Width
        .ShapeRange.Height = Range("A1").Height
    End With
End Sub
