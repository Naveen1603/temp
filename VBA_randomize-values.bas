Function MaskData(columnValue As Variant, dataType As Integer, seed As Long) As Variant
    ' Function to mask data based on data type
    
    ' Check data type and apply masking accordingly
    Select Case dataType
        Case dbText, dbChar ' Text (String)
            MaskData = ShuffleString(CStr(columnValue), seed)
            
        Case dbMemo ' Memo (Long Text)
            ' Handle Long Text data type (if needed)
            ' Example: Shuffle the first 10 characters
            MaskData = ShuffleString(Left(CStr(columnValue), 10), seed)
            
        Case dbInteger, dbLong, dbBigInt ' Numeric
            MaskData = RandomNumericOperation(columnValue, seed)
            
        Case dbFloat, dbDouble, dbDecimal ' Floating-point Numeric
            MaskData = RandomNumericOperation(columnValue, seed)
            
        Case dbDate, dbTime, dbTimeStamp, dbDateTimeExtended ' Date/Time
            MaskData = RandomDateOperation(columnValue, seed)
            
        Case dbBoolean ' Boolean
            ' Example: Generate a random boolean value
            Randomize seed
            MaskData = (Int(Rnd() * 2) = 0)
            
        Case dbCurrency ' Currency
            ' Example: Multiply the currency value by a random number between 0.5 and 1.5
            Randomize seed
            MaskData = columnValue * (0.5 + Rnd())
            
        Case dbByte, dbBinary, dbLongBinary, dbVarBinary ' Binary data
            ' Example: Leave these types unchanged
            MaskData = columnValue
        
        ' Add more cases for other data types as needed
        
        Case Else
            ' For unsupported types, leave the value unchanged
            MaskData = columnValue
    End Select
End Function



Function ShuffleString(inputString As String, seed As Long) As String
    ' Function to randomly shuffle characters in a string
    Dim i As Integer
    Dim randIndex As Integer
    Dim tempChar As String
    Dim charArray() As String
    
    ' Convert the string to an array of characters
    ReDim charArray(1 To Len(inputString))
    For i = 1 To Len(inputString)
        charArray(i) = Mid(inputString, i, 1)
    Next i
    
    ' Shuffle the characters in the array
    Randomize seed
    For i = UBound(charArray) To LBound(charArray) + 1 Step -1
        randIndex = Int((i - 1) * Rnd() + 1)
        tempChar = charArray(i)
        charArray(i) = charArray(randIndex)
        charArray(randIndex) = tempChar
    Next i
    
    ' Convert the array back to a string
    ShuffleString = Join(charArray, "")
End Function

Function RandomNumericOperation(inputValue As Variant, seed As Long) As Variant
    ' Function to perform a random numeric operation
    Randomize seed
    ' Example: Multiply the value by a random number between 0.5 and 1.5
    RandomNumericOperation = inputValue * (0.5 + Rnd())
End Function

Function RandomDateOperation(inputDate As Variant, seed As Long) As Variant
    ' Function to perform a random date operation
    Randomize seed
    ' Example: Add/subtract a random number of days (up to 5 days)
    RandomDateOperation = DateAdd("d", Int((10 * Rnd()) - 5), inputDate)
End Function
