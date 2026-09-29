#pragma once

#include "Commandlets/Commandlet.h"
#include "DestructionTraceExportCommandlet.generated.h"

/** DP-01 offline task dependency export; the analysis implementation is editor-only. */
UCLASS()
class MERIDIANSQUAD_API UDestructionTraceExportCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    UDestructionTraceExportCommandlet();
    virtual int32 Main(const FString& Params) override;
};
